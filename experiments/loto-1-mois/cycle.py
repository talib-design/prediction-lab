#!/usr/bin/env python3
"""Expérience « Loto, 1 mois » : une prédiction, un tirage, une analyse, un apprentissage.

Stdlib uniquement (Python >= 3.10), pour tourner sans environnement virtuel.

Trois grilles par tirage, figées dans le protocole (PROTOCOLE.md) :
  - adaptatif : fréquence pondérée dans le temps ; ses deux paramètres (demi-vie, mode
    chaud/froid) sont re-sélectionnés après CHAQUE tirage, selon leur performance sur
    les 30 derniers tirages. C'est la grille qui « apprend ».
  - frequence : fréquence sur tout l'historique, jamais modifiée (modèle du Milestone 1).
  - hasard    : grille aléatoire, graine = date du tirage. Le témoin.

Commandes :
  add-result DATE n1 n2 n3 n4 n5 CHANCE --source URL --source2 URL
  score                 note toutes les prédictions dont le tirage est connu
  learn                 re-sélectionne les paramètres de la grille adaptative
  predict DATE          enregistre les 3 grilles pour un tirage futur
  status                bilan cumulé (écrit aussi BILAN.md)
  verify                vérifie la chaîne de hachage du journal
  add-rapports DATE r1 … r9 --source URL --source2 URL
                        gains officiels par rang du 1er tirage (« - » = pas de gagnant)
  next                  état du cycle : tirages à rattraper, prochaine cible, prédiction autorisée ?

Simulation financière (amendement du 26/09/2026) : chaque grille est jouée fictivement
à MISE € (grille simple, sans 2nd tirage). Les gains sont les rapports officiels du tirage.
Les codes LOTO (tirage au sort de 20 000 €) ne sont pas simulables et sont exclus.

Garde-fous de predict (amendement du 26/09/2026, avant tout score) :
  - le tirage régulier qui précède la cible doit déjà être dans historique.csv ;
  - learn doit avoir tourné après ce tirage (etat_adaptatif.json à jour) ;
  - la cible ne peut pas être passée, ni être le tirage du jour après 20h00 (Paris).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import sys
from datetime import date, datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
HIST = HERE / "historique.csv"
JOURNAL = HERE / "journal.jsonl"
STATE = HERE / "etat_adaptatif.json"
BILAN = HERE / "BILAN.md"

N_MAIN, K_MAIN, N_CHANCE = 49, 5, 10
DRAW_WEEKDAYS = {0, 2, 5}  # lundi, mercredi, samedi
START, END = date(2026, 9, 26), date(2026, 10, 26)
GRIDS = ("adaptatif", "frequence", "hasard")
HALF_LIVES = (10, 25, 50, 100, 300, None)  # None = pas d'oubli
MODES = ("chaud", "froid")
SELECTION_WINDOW = 30
E_MATCH = K_MAIN * K_MAIN / N_MAIN  # 0.5102 bon numéro attendu par grille
MISE = 2.20  # prix d'une grille simple Loto (fdj.fr, comment jouer), 2nd tirage non joué
CUTOFF_HOUR = 20  # heure de Paris après laquelle on ne prédit plus le tirage du jour
PUBLISH = (20, 45)  # heure de Paris à partir de laquelle le résultat du jour est publié


def paris_now() -> datetime:
    """Heure de Paris sans dépendre de tzdata : CEST du dernier dimanche de mars au
    dernier dimanche d'octobre (01:00 UTC), CET sinon."""
    from datetime import timedelta
    now = datetime.now(timezone.utc)

    def last_sunday(y, m):
        d = date(y, m, 31)
        return d - timedelta(days=(d.weekday() + 1) % 7)

    y = now.year
    start = datetime(y, 3, last_sunday(y, 3).day, 1, tzinfo=timezone.utc)
    end = datetime(y, 10, last_sunday(y, 10).day, 1, tzinfo=timezone.utc)
    off = 2 if start <= now < end else 1
    return (now + timedelta(hours=off)).replace(tzinfo=None)


def prev_draw_day(d: date) -> date:
    from datetime import timedelta
    d -= timedelta(days=1)
    while d.weekday() not in DRAW_WEEKDAYS:
        d -= timedelta(days=1)
    return d


def next_draw_day(d: date) -> date:
    from datetime import timedelta
    d += timedelta(days=1)
    while d.weekday() not in DRAW_WEEKDAYS:
        d += timedelta(days=1)
    return d


def period_draws() -> list[date]:
    out, d = [], START
    while d <= END:
        if d.weekday() in DRAW_WEEKDAYS:
            out.append(d)
        d = next_draw_day(d)
    return out


def die(msg: str) -> None:
    print(f"ERREUR : {msg}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------- données
def load_history() -> list[tuple[date, list[int], int]]:
    rows = []
    with HIST.open() as f:
        for r in csv.DictReader(f):
            main = sorted(int(r[f"n{i}"]) for i in range(1, 6))
            rows.append((date.fromisoformat(r["date"]), main, int(r["chance"])))
    rows.sort(key=lambda x: x[0])
    return rows


def load_journal() -> list[dict]:
    if not JOURNAL.exists():
        return []
    return [json.loads(line) for line in JOURNAL.read_text().splitlines() if line.strip()]


def _hash(rec: dict) -> str:
    body = {k: v for k, v in rec.items() if k != "record_hash"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def append(event: dict) -> dict:
    j = load_journal()
    event["created_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    event["prev_hash"] = j[-1]["record_hash"] if j else "0" * 64
    event["record_hash"] = _hash(event)
    with JOURNAL.open("a") as f:
        f.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")
    return event


def verify() -> None:
    prev = "0" * 64
    for i, rec in enumerate(load_journal()):
        if rec["prev_hash"] != prev or _hash(rec) != rec["record_hash"]:
            die(f"chaîne rompue à la ligne {i + 1}")
        prev = rec["record_hash"]
    print("journal intègre")


# ---------------------------------------------------------------- modèles
def weighted_scores(hist, half_life, pool: str) -> list[float]:
    n = N_MAIN if pool == "main" else N_CHANCE
    s = [0.0] * (n + 1)
    lam = 1.0 if half_life is None else 0.5 ** (1 / half_life)
    w = 1.0
    for _, main, chance in reversed(hist):
        for x in main if pool == "main" else [chance]:
            s[x] += w
        w *= lam
    return s


def ticket_from(scores: list[float], k: int, mode: str) -> list[int]:
    nums = range(1, len(scores))
    key = (lambda x: (-scores[x], x)) if mode == "chaud" else (lambda x: (scores[x], x))
    return sorted(sorted(nums, key=key)[:k])


def probs_from(scores: list[float], k: int, mode: str) -> list[float]:
    """Probabilités d'inclusion implicites (pour la « masse » du score d'apprentissage)."""
    v = scores[1:]
    if mode == "froid":
        m = max(v)
        v = [m - x for x in v]
    tot = sum(v) or 1.0
    p = [k * x / tot for x in v]
    # lissage vers l'uniforme pour éviter les zéros
    return [0.9 * x + 0.1 * k / len(v) for x in p]


def select_params(hist) -> tuple[dict, list[dict]]:
    """Re-sélection walk-forward sur les SELECTION_WINDOW derniers tirages."""
    table = []
    for hl in HALF_LIVES:
        for mode in MODES:
            hits = 0
            mass = 0.0
            for i in range(len(hist) - SELECTION_WINDOW, len(hist)):
                past, (_, main, _) = hist[:i], hist[i]
                sc = weighted_scores(past, hl, "main")
                hits += len(set(ticket_from(sc, K_MAIN, mode)) & set(main))
                p = probs_from(sc, K_MAIN, mode)
                mass += sum(p[x - 1] for x in main)
            table.append({"half_life": hl, "mode": mode, "hits": hits,
                          "lift": round(mass / (SELECTION_WINDOW * K_MAIN * K_MAIN / N_MAIN), 4)})
    best = max(table, key=lambda r: (r["hits"], r["lift"]))
    return {"half_life": best["half_life"], "mode": best["mode"]}, table


def build_grids(hist, target: date) -> dict:
    state = json.loads(STATE.read_text())
    hl, mode = state["half_life"], state["mode"]
    grids = {
        "adaptatif": {
            "main": ticket_from(weighted_scores(hist, hl, "main"), K_MAIN, mode),
            "chance": ticket_from(weighted_scores(hist, hl, "chance"), 1, mode)[0],
            "params": {"half_life": hl, "mode": mode},
        },
        "frequence": {
            "main": ticket_from(weighted_scores(hist, None, "main"), K_MAIN, "chaud"),
            "chance": ticket_from(weighted_scores(hist, None, "chance"), 1, "chaud")[0],
        },
    }
    rng = random.Random(int(hashlib.sha256(target.isoformat().encode()).hexdigest(), 16))
    grids["hasard"] = {"main": sorted(rng.sample(range(1, N_MAIN + 1), K_MAIN)),
                       "chance": rng.randint(1, N_CHANCE), "seed": f"sha256({target})"}
    return grids


# ---------------------------------------------------------------- scoring
def rank(hits: int, chance_ok: bool) -> str:
    table = {(5, 1): "rang 1", (5, 0): "rang 2", (4, 1): "rang 3", (4, 0): "rang 4",
             (3, 1): "rang 5", (3, 0): "rang 6", (2, 1): "rang 7", (2, 0): "rang 8",
             (1, 1): "rang 9 (remboursé)", (0, 1): "rang 9 (remboursé)"}
    return table.get((hits, int(chance_ok)), "perdu")


def hypergeom_pmf() -> list[float]:
    c = math.comb
    return [c(K_MAIN, i) * c(N_MAIN - K_MAIN, K_MAIN - i) / c(N_MAIN, K_MAIN) for i in range(K_MAIN + 1)]


def p_value_at_least(total: int, n: int) -> float:
    """P(somme des bons numéros sur n grilles au hasard >= total), exacte."""
    pmf, dist = hypergeom_pmf(), [1.0]
    for _ in range(n):
        new = [0.0] * (len(dist) + K_MAIN)
        for s, ps in enumerate(dist):
            for i, pi in enumerate(pmf):
                new[s + i] += ps * pi
        dist = new
    return sum(dist[total:])


def rank_index(rang: str) -> int | None:
    return int(rang.split()[1]) if rang.startswith("rang ") else None


def rank_probs() -> dict[int, float]:
    """Probabilité de chaque rang pour une grille au hasard (1er tirage)."""
    pmf = hypergeom_pmf()
    pc = 1 / N_CHANCE
    return {1: pmf[5] * pc, 2: pmf[5] * (1 - pc), 3: pmf[4] * pc, 4: pmf[4] * (1 - pc),
            5: pmf[3] * pc, 6: pmf[3] * (1 - pc), 7: pmf[2] * pc, 8: pmf[2] * (1 - pc),
            9: (pmf[1] + pmf[0]) * pc}


def load_rapports() -> dict[str, dict]:
    out = {}
    for e in load_journal():
        if e["type"] == "rapports":
            out[e["target_date"]] = e["rapports"]
    return out


def euros(x: float) -> str:
    return f"{x:,.2f} €".replace(",", " ").replace(".", ",")


# ---------------------------------------------------------------- commandes
def cmd_add_result(a) -> None:
    d = date.fromisoformat(a.date)
    main = sorted(a.numbers[:5])
    ch = a.numbers[5]
    if len(set(main)) != 5 or not all(1 <= x <= N_MAIN for x in main) or not 1 <= ch <= N_CHANCE:
        die("combinaison invalide")
    if d.weekday() not in DRAW_WEEKDAYS:
        die(f"{d} n'est pas un jour de tirage régulier")
    if not a.source2 or a.source == a.source2:
        die("deux sources distinctes sont exigées")
    hist = load_history()
    for hd, hm, hc in hist:
        if hd == d:
            if hm == main and hc == ch:
                print(f"{d} déjà présent, identique")
                return
            die(f"{d} déjà présent avec une AUTRE combinaison : {hm} + {hc}")
    with HIST.open("a") as f:
        f.write(f"{d}," + ",".join(map(str, main)) + f",{ch},web:{a.source} | {a.source2}\n")
    append({"type": "resultat", "target_date": str(d), "main": main, "chance": ch,
            "sources": [a.source, a.source2]})
    print(f"résultat {d} enregistré : {main} + {ch}")


def cmd_add_rapports(a) -> None:
    d = date.fromisoformat(a.date)
    if d not in {hd for hd, _, _ in load_history()}:
        die(f"{d} absent de historique.csv : lance d'abord add-result")
    if not a.source2 or a.source == a.source2:
        die("deux sources distinctes sont exigées")
    vals = {}
    for i, v in enumerate(a.values, start=1):
        v = v.strip().replace("€", "").replace("\u202f", "").replace(" ", "").replace(",", ".")
        if v in ("-", "0", ""):
            vals[str(i)] = None
        else:
            try:
                vals[str(i)] = round(float(v), 2)
            except ValueError:
                die(f"rapport du rang {i} illisible : {v!r}")
    if vals["9"] is None or abs(vals["9"] - MISE) > 0.001:
        print(f"ATTENTION : rang 9 = {vals['9']} (attendu {MISE} €, remboursement de la mise)")
    known = load_rapports().get(str(d))
    if known is not None:
        if known == vals:
            print(f"rapports du {d} déjà présents, identiques")
            return
        die(f"rapports du {d} déjà présents avec d'AUTRES valeurs : {known}")
    append({"type": "rapports", "target_date": str(d), "rapports": vals, "mise": MISE,
            "sources": [a.source, a.source2]})
    print(f"rapports enregistrés pour le {d} : " + ", ".join(f"r{k}={v}" for k, v in vals.items()))


def cmd_predict(a) -> None:
    target = date.fromisoformat(a.date)
    if target.weekday() not in DRAW_WEEKDAYS:
        die(f"{target} n'est pas un jour de tirage")
    hist = load_history()
    if any(d >= target for d, _, _ in hist):
        die(f"le tirage du {target} (ou un plus récent) est déjà connu : prédiction refusée")
    if any(e["type"] == "prediction" and e["target_date"] == str(target) for e in load_journal()):
        die(f"une prédiction existe déjà pour {target} (immuable)")
    now = paris_now()
    if target < now.date() or (target == now.date() and now.hour >= CUTOFF_HOUR):
        die(f"le tirage du {target} est passé ou imminent (il est {now:%Y-%m-%d %H:%M} à Paris) : prédiction refusée")
    known = {d for d, _, _ in hist}
    prev = prev_draw_day(target)
    if prev not in known:
        die(f"le tirage précédent ({prev}) n'est pas encore enregistré : lance d'abord add-result, "
            f"score et learn, puis prédit {target}")
    state = json.loads(STATE.read_text())
    if state.get("selected_after") != str(hist[-1][0]):
        die(f"learn n'a pas tourné après le dernier tirage enregistré ({hist[-1][0]}) : lance cycle.py learn")
    grids = build_grids(hist, target)
    append({"type": "prediction", "target_date": str(target), "grids": grids,
            "training_last_draw": str(hist[-1][0]), "n_training_draws": len(hist)})
    print(f"prédiction enregistrée pour le {target}")
    for g in GRIDS:
        print(f"  {g:<10} {grids[g]['main']}  chance {grids[g]['chance']}")


def cmd_score(_a) -> None:
    hist = {d: (m, c) for d, m, c in load_history()}
    j = load_journal()
    done = {e["target_date"] for e in j if e["type"] == "score"}
    n = 0
    for e in j:
        if e["type"] != "prediction" or e["target_date"] in done:
            continue
        d = date.fromisoformat(e["target_date"])
        if d not in hist:
            print(f"{d} : résultat pas encore enregistré")
            continue
        main, ch = hist[d]
        res = {}
        for g in GRIDS:
            t = e["grids"][g]
            hits = sorted(set(t["main"]) & set(main))
            res[g] = {"hits": len(hits), "numeros_trouves": hits, "chance_ok": t["chance"] == ch,
                      "rang": rank(len(hits), t["chance"] == ch)}
        append({"type": "score", "target_date": str(d), "draw": {"main": main, "chance": ch},
                "results": res})
        n += 1
        print(f"{d}  tirage {main} + {ch}")
        for g in GRIDS:
            r = res[g]
            print(f"  {g:<10} {r['hits']}/5 {r['numeros_trouves']}  chance {'OK' if r['chance_ok'] else 'non'}  → {r['rang']}")
    if not n:
        print("rien de nouveau à noter")


def cmd_learn(_a) -> None:
    hist = load_history()
    old = json.loads(STATE.read_text()) if STATE.exists() else None
    new, table = select_params(hist)
    new["selected_after"] = str(hist[-1][0])
    STATE.write_text(json.dumps(new, indent=2) + "\n")
    append({"type": "apprentissage", "after_draw": str(hist[-1][0]),
            "old": old, "new": new, "window": SELECTION_WINDOW, "table": table})
    changed = old is None or (old["half_life"], old["mode"]) != (new["half_life"], new["mode"])
    print(f"paramètres {'CHANGÉS' if changed else 'inchangés'} : {old and {k: old[k] for k in ('half_life','mode')}} → "
          f"demi-vie {new['half_life']}, mode {new['mode']}")
    for r in sorted(table, key=lambda r: (-r["hits"], -r["lift"]))[:5]:
        print(f"  hl={str(r['half_life']):<5} {r['mode']:<6} {r['hits']} bons numéros / {SELECTION_WINDOW} tirages "
              f"(hasard ≈ {SELECTION_WINDOW * E_MATCH:.1f}), lift {r['lift']}")


def cmd_status(_a) -> None:
    scores = [e for e in load_journal() if e["type"] == "score"]
    lines = ["# Bilan cumulé — Loto 1 mois", "",
             f"Mis à jour : {datetime.now(timezone.utc).isoformat(timespec='minutes')} UTC · "
             f"{len(scores)} tirage(s) noté(s). Attendu au hasard : {E_MATCH:.2f} bon numéro par grille "
             f"et par tirage, numéro chance 1 fois sur 10.", "",
             "| Grille | Bons numéros | Attendu (hasard) | Chance trouvée | Grilles gagnantes | p (≥ observé si hasard) |",
             "|---|---|---|---|---|---|"]
    for g in GRIDS:
        hits = sum(s["results"][g]["hits"] for s in scores)
        ch = sum(s["results"][g]["chance_ok"] for s in scores)
        win = sum(s["results"][g]["rang"] != "perdu" for s in scores)
        p = p_value_at_least(hits, len(scores)) if scores else float("nan")
        lines.append(f"| {g} | {hits} | {len(scores) * E_MATCH:.1f} | {ch}/{len(scores)} | {win}/{len(scores)} | {p:.2f} |")
    # ------------------------------------------------ simulation financière
    rap = load_rapports()
    probs = rank_probs()
    fin = [s for s in scores if s["target_date"] in rap]
    missing = [s["target_date"] for s in scores if s["target_date"] not in rap]
    ev, ev_note = 0.0, False
    for s in fin:
        r = rap[s["target_date"]]
        for k, pr in probs.items():
            if r[str(k)] is None:
                ev_note = True
            else:
                ev += pr * r[str(k)]
    lines += ["", f"## Simulation financière (fictive, {euros(MISE)} par grille, 1er tirage seul)", "",
              f"{len(fin)} tirage(s) avec rapports officiels" +
              (f" · rapports manquants : {', '.join(missing)}" if missing else "") + ".", "",
              "| Grille | Mise | Gains | Net | Retour (gains / mise) |", "|---|---|---|---|---|"]
    undet = []
    for g in GRIDS:
        gain = 0.0
        for s in fin:
            k = rank_index(s["results"][g]["rang"])
            if k is not None:
                v = rap[s["target_date"]][str(k)]
                if v is None:
                    undet.append(f"{g} le {s['target_date']} (rang {k} sans autre gagnant)")
                else:
                    gain += v
        mise = MISE * len(fin)
        ret = f"{gain / mise:.0%}" if mise else "—"
        lines.append(f"| {g} | {euros(mise)} | {euros(gain)} | {euros(gain - mise)} | {ret} |")
    if fin:
        lines.append(f"| *espérance d'une grille au hasard* | {euros(MISE * len(fin))} | {euros(ev)} | "
                     f"{euros(ev - MISE * len(fin))} | {ev / (MISE * len(fin)):.0%} |")
    notes = []
    if ev_note:
        notes.append("Espérance calculée sans les rangs restés sans gagnant (jackpot le plus souvent) : "
                     "elle est donc sous-estimée. Le jackpot seul vaut, par grille, son montant ÷ 19 068 840 combinaisons, "
                     "soit ~0,26 € pour 5 M€.")
    if undet:
        notes.append("Gain non déterminable (à compléter à la main dans le rapport final) : " + "; ".join(undet) + ".")
    notes.append("Codes LOTO (20 000 €) et 2nd tirage exclus. Aucune mise réelle.")
    lines += [""] + notes

    lines += ["", "| Tirage | Combinaison | adaptatif | frequence | hasard |", "|---|---|---|---|---|"]
    for s in scores:
        dr = s["draw"]
        r = rap.get(s["target_date"])

        def cell(g):
            res = s["results"][g]
            c = f"{res['hits']}/5{' +C' if res['chance_ok'] else ''}"
            k = rank_index(res["rang"])
            if k is not None:
                v = r and r[str(k)]
                c += f" · {euros(v)}" if v else f" · rang {k}"
            return c
        cells = [cell(g) for g in GRIDS]
        lines.append(f"| {s['target_date']} | {'-'.join(map(str, dr['main']))} + {dr['chance']} | " + " | ".join(cells) + " |")
    BILAN.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def cmd_next(_a) -> None:
    now = paris_now()
    hist = load_history()
    known = {d for d, _, _ in hist}
    j = load_journal()
    predicted = {e["target_date"] for e in j if e["type"] == "prediction"}
    scored = {e["target_date"] for e in j if e["type"] == "score"}
    published = lambda d: d < now.date() or (d == now.date() and (now.hour, now.minute) >= PUBLISH)
    print(f"heure de Paris : {now:%Y-%m-%d %H:%M} · dernier tirage enregistré : {hist[-1][0]}")
    todo = [d for d in period_draws() if d not in known and published(d)]
    pending = [d for d in period_draws() if d not in known and not published(d) and d == now.date()]
    print("à rattraper (publiés, non enregistrés) : " + (", ".join(map(str, todo)) or "aucun"))
    if pending:
        print(f"tirage du jour {pending[0]} : pas encore publié (après {PUBLISH[0]}h{PUBLISH[1]:02d})")
    unscored = sorted(t for t in predicted if t not in scored and date.fromisoformat(t) in known)
    if unscored:
        print("prédictions à noter (lancer score) : " + ", ".join(unscored))
    rap = load_rapports()
    no_rap = [str(d) for d in period_draws() if d in known and str(d) not in rap]
    if no_rap:
        print("rapports à ajouter (add-rapports) : " + ", ".join(no_rap))
    state = json.loads(STATE.read_text())
    if state.get("selected_after") != str(hist[-1][0]):
        print(f"learn à relancer (dernier apprentissage après {state.get('selected_after')})")
    missed = [str(d) for d in period_draws() if str(d) not in predicted and d in known]
    if missed:
        print("tirages de la période restés sans prédiction : " + ", ".join(missed))
    if END in known:
        print("VERDICT : période terminée, dernier tirage enregistré → rapport final")
        return
    target = next_draw_day(hist[-1][0])
    if str(target) in predicted:
        print(f"VERDICT : prédiction déjà enregistrée pour {target} → rien à prédire")
    elif target > END:
        print("VERDICT : hors période → rien à prédire")
    elif target < now.date() or (target == now.date() and now.hour >= CUTOFF_HOUR):
        print(f"VERDICT : cible {target} déjà tirée ou imminente → rattraper d'abord ; elle restera sans prédiction")
    elif state.get("selected_after") != str(hist[-1][0]):
        print(f"VERDICT : lancer learn, puis predict {target}")
    else:
        print(f"VERDICT : predict {target}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add-result")
    p.add_argument("date")
    p.add_argument("numbers", type=int, nargs=6)
    p.add_argument("--source", required=True)
    p.add_argument("--source2", required=True)
    p.set_defaults(f=cmd_add_result)
    p = sub.add_parser("add-rapports")
    p.add_argument("date")
    p.add_argument("values", nargs=9, metavar="r1..r9")
    p.add_argument("--source", required=True)
    p.add_argument("--source2", required=True)
    p.set_defaults(f=cmd_add_rapports)
    p = sub.add_parser("predict")
    p.add_argument("date")
    p.set_defaults(f=cmd_predict)
    for name, f in (("score", cmd_score), ("learn", cmd_learn), ("status", cmd_status),
                    ("verify", lambda _a: verify()), ("next", cmd_next)):
        sub.add_parser(name).set_defaults(f=f)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
