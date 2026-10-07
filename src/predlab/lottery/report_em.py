"""Markdown report of the EuroMillions study, rebuilt from the JSON outputs.

Order follows the Loto M1 report: what could have been detected comes first, because it
bounds what every later "nothing found" can mean. Then the pure-chance control, which
says whether the lab itself can be trusted, then the results.
"""

from __future__ import annotations

from typing import Any

from predlab.lottery.gamespec import EM_2004_02, EM_2011_05, EM_2016_09, EM_MAIN_2004
from predlab.lottery.power import minimum_detectable_effect

LABELS = {
    "frequency": "fréquence totale",
    "rolling_frequency_100": "fréquence 100 derniers",
    "rolling_frequency_300": "fréquence 300 derniers",
    "shrunk_frequency": "fréquence rétrécie",
    "gap": "retard",
    "hot50": "chauds 50",
    "cold50": "froids 50",
    "repeat": "répétition",
    "temoin_r1": "témoin hasard (R1)",
}


def _f(x: float | None, digits: int = 3) -> str:
    if x is None:
        return "–"
    return f"{x:.{digits}f}".replace(".", ",")


def _p(x: float | None) -> str:
    if x is None:
        return "–"
    if x < 0.001:
        return "< 0,001"
    return _f(x, 3)


def _z(x: float) -> str:
    return f"{x:+.2f}".replace(".", ",")


def _z5(x: float) -> str:
    return f"{x:+.5f}".replace(".", ",")


def _n(x: int) -> str:
    return f"{x:,}".replace(",", " ")


def _pct(x: float, digits: int = 0) -> str:
    return f"{x * 100:+.{digits}f} %".replace(".", ",")


def power_section() -> list[str]:
    rows = [
        ("boules, 2004-2026", EM_MAIN_2004.pool("main"), 1987),
        ("boules, ère 2016-09", EM_2016_09.pool("main"), 1047),
        ("étoiles 1-12, 2016-09", EM_2016_09.pool("stars"), 1047),
        ("étoiles 1-11, 2011-05", EM_2011_05.pool("stars"), 562),
        ("étoiles 1-9, 2004-02", EM_2004_02.pool("stars"), 378),
    ]
    out = [
        "## 1. Ce qu'on pouvait détecter",
        "",
        "À lire avant les résultats : ce tableau borne ce que « rien de détecté » veut dire. "
        "Biais minimal sur un numéro, vu 8 fois sur 10 au seuil de 5 %.",
        "",
        "| Groupe | Tirages | Sans correction | Corrigé (tous les numéros) |",
        "|---|---|---|---|",
    ]
    for label, pool, n in rows:
        a = minimum_detectable_effect(pool, n, multiplicity_correction=False)
        b = minimum_detectable_effect(pool, n, multiplicity_correction=True)
        out.append(f"| {label} | {_n(n)} | {_pct(a.relative_effect)} | {_pct(b.relative_effect)} |")
    out += [
        "",
        "Pour les théories (section 4), la dernière colonne de leur tableau donne l'effet "
        "minimal détectable de chaque test : autour de +5 % pour les boules, +10 % pour les "
        "étoiles. Un effet plus petit peut exister sans qu'on puisse le voir avec 22 ans de "
        "tirages.",
        "",
    ]
    return out


def control_section(control: dict[str, Any] | None) -> list[str]:
    out = ["## 2. Contrôle 100 % hasard (em-R2)", ""]
    if not control:
        return [*out, "Pas encore lancé (`predlab lottery control`).", ""]
    verdict = "réussi" if control["passed"] else "ÉCHEC — conclusions suspendues"
    out += [
        f"Toute la batterie relancée sur {control['histories']} historiques fabriqués au "
        f"hasard ({control['tests_per_history']} tests chacun). Verdict : **{verdict}**.",
        "",
        "| Critère inscrit | Seuil | Mesuré |",
        "|---|---|---|",
        f"| part des p < 0,05 | entre 3 % et 7 % | {_f(control['nominal_rate'] * 100, 2)} % |",
    ]
    for fam, frac in control["histories_with_survivor"].items():
        out.append(
            f"| historiques avec un « signal » après BH, {fam} | <= 8 % | {_f(frac * 100, 1)} % |"
        )
    out += [
        f"| uniformité des p des théories (KS) | p > 0,01 | {_p(control['ks_p_family_b'])} |",
        "",
    ]
    return out


def mechanism_section(results: list[dict[str, Any]], summary: dict[str, Any]) -> list[str]:
    out = [
        "## 3. Le mécanisme est-il équitable ? (A1 à A4)",
        "",
        "| Test | Tirages | p | q (BH) |",
        "|---|---|---|---|",
    ]
    for r in results:
        if r["family"] in ("A1", "A4"):
            out.append(
                f"| {r['label']} | {r['n_draws']} | {_p(r['p_value'])} | {_p(r['q_value'])} |"
            )
    a2 = sorted((r for r in results if r["family"] == "A2"), key=lambda r: r["p_value"])[:3]
    out += [
        "",
        f"Numéro par numéro (A2) : {summary['A2']['nominal_p_lt_0_05']} tests sur "
        f"{summary['A2']['tests']} à p < 0,05, pour {_f(summary['A2']['expected_by_chance'], 1)} "
        f"attendus au hasard ; {summary['A2']['bh_survivors']} après correction. Les plus "
        "extrêmes :",
        "",
    ]
    for r in a2:
        out.append(
            f"- {r['label']} : {int(r['observed'])} sorties pour {_f(r['expected'], 1)} "
            f"attendues (p = {_p(r['p_value'])}, q = {_p(r['q_value'])})."
        )
    out += [
        "",
        f"Ordre d'extraction (A3) : {summary['A3']['nominal_p_lt_0_05']} test sur "
        f"{summary['A3']['tests']} à p < 0,05, {summary['A3']['bh_survivors']} après correction.",
        "",
    ]
    return out


def theories_section(results: list[dict[str, Any]]) -> list[str]:
    out = [
        "## 4. Les théories de prédiction (B) : chaud, froid, séries, retard",
        "",
        "Test causal exact : à chaque tirage la règle ne regarde que le passé ; "
        "« ratio » = sorties des numéros choisis / sorties attendues au hasard "
        "(1,000 = pareil que le hasard). « 1re / 2e moitié » : avant / depuis 2020.",
        "",
        "| Théorie | Tirages | Ratio | z | p | q | z 1re / 2e moitié | Détectable |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        if r["family"] != "B":
            continue
        d = r["detail"]
        out.append(
            f"| {r['label']} | {r['n_draws']} | {_f(d['ratio'])} | {_z(r['statistic'])} | "
            f"{_p(r['p_value'])} | {_p(r['q_value'])} | {_z(d['early']['z'])} / "
            f"{_z(d['late']['z'])} | {_f(d['detectable_ratio'])} |"
        )
    return [*out, ""]


def shape_section(results: list[dict[str, Any]]) -> list[str]:
    out = [
        "## 5. La forme des tirages (C)",
        "",
        "| Test | Observé | Hasard exact | p | q |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        if r["family"] in ("C1", "C2", "C3"):
            out.append(
                f"| {r['label']} | {_f(r['observed'])} | {_f(r['expected'])} | "
                f"{_p(r['p_value'])} | {_p(r['q_value'])} |"
            )
    c2 = next((r for r in results if r["family"] == "C2"), None)
    if c2:
        out += [
            "",
            f"Combinaisons répétées : {int(c2['observed'])} paire de tirages identiques "
            f"({_repeats(c2)}) pour {_f(c2['expected'], 2)} attendue au hasard ; "
            f"{c2['detail']['pairs_sharing_exactly_4']} paires partagent 4 boules pour "
            f"{_f(c2['detail']['expected_pairs_sharing_4'], 1)} attendues.",
        ]
    return [*out, ""]


def _repeats(c2: dict[str, Any]) -> str:
    items = c2["detail"].get("repeated", [])
    return (
        "; ".join(
            f"{'-'.join(map(str, it['balls']))} les {' et '.join(it['dates'])}" for it in items
        )
        or "–"
    )


def backtest_section(bt: dict[str, Any] | None) -> list[str]:
    out = ["## 6. Logiques contre hasard, en marche avant (D1, R1)", ""]
    if not bt:
        return [*out, "Pas encore lancé (`predlab lottery backtest`).", ""]
    out += [
        "Chaque logique joue une grille par tirage, calculée uniquement avec les tirages "
        "précédents. « Percentile » : part des 1 000 joueurs au hasard qu'elle dépasse. "
        "« Log loss » : coût de ses probabilités par rapport au tirage uniforme (négatif = "
        "mieux que le hasard).",
        "",
    ]
    for key, title in (("balls_2004", "Boules, 2004-2026"), ("grid_2016_09", "Ère 2016-09")):
        block = bt[key]
        for pool, info in block["pools"].items():
            name = "boules" if pool == "main" else "étoiles"
            heading = title if key == "balls_2004" else f"{title}, {name}"
            rp = info["random_players"]["mean_matches_quantiles"]
            out += [
                f"**{heading}** ({_n(block['n_targets'])} tirages, du {block['first_target']} "
                f"au {block['last_target']}). Hasard : {_f(info['expected_matches'])} trouvés "
                f"par tirage ; 95 % des joueurs au hasard entre {_f(rp['0.025'])} et {_f(rp['0.975'])}.",
                "",
                "| Logique | Trouvés | z | Percentile | Log loss vs uniforme [IC 95 %] | q |",
                "|---|---|---|---|---|---|",
            ]
            for lg in info["logics"]:
                lo, hi = lg["logloss_ci"]
                out.append(
                    f"| {LABELS.get(lg['logic'], lg['logic'])} | {_f(lg['mean_matches'])} | "
                    f"{_z(lg['matches_z'])} | {lg['percentile_vs_players'] * 100:.0f} % | "
                    f"{_z5(lg['logloss_diff'])} [{_z5(lo)} ; {_z5(hi)}] | {_p(lg['logloss_q'])} |"
                )
            w = info["witness_r1"]
            out += [
                f"| témoin hasard (R1) | {_f(w['mean_matches'])} | {w['z']:+.2f} | – | – | – |",
                "",
            ]
    return out


def payout_section(bt: dict[str, Any] | None) -> list[str]:
    if not bt:
        return []
    p = bt["payouts_2016_09"]
    rp = p["random_players"]["mean_payout_quantiles"]
    out = [
        "## 7. Gains fictifs, une grille par tirage (D2)",
        "",
        f"Ère 2016-09, {p['n_draws']} tirages, grille à {_f(p['price_eur'], 2)} EUR (prix lu sur la "
        "page FDJ le 2026-10-06 ; constance sur toute la période non vérifiée). Payée au rapport "
        "officiel. Le jackpot n'apparaît pas : aucune grille ne l'a touché. Mesure de "
        "performance, pas une stratégie de mise.",
        "",
        f"1 000 joueurs au hasard : gain moyen médian {_f(rp['0.5'], 2)} EUR par grille "
        f"(95 % entre {_f(rp['0.025'], 2)} et {_f(rp['0.975'], 2)}), rendement médian "
        f"{_pct(p['random_players']['roi_median'])}.",
        "",
        "| Logique | Gain moyen / grille | IC 95 % | Rendement | Grilles gagnantes | Percentile |",
        "|---|---|---|---|---|---|",
    ]
    rows = [*p["logics"].items(), ("temoin_r1", {**p["witness_r1"], "percentile_vs_players": None})]
    for name, info in rows:
        pct = info.get("percentile_vs_players")
        out.append(
            f"| {LABELS.get(name, name)} | {_f(info['mean_payout_eur'], 3)} EUR | "
            f"{_f(info['ci95'][0], 2)}-{_f(info['ci95'][1], 2)} | {_pct(info['roi'])} | "
            f"{info['wins']} | {'–' if pct is None else f'{pct * 100:.0f} %'} |"
        )
    check = bt.get("rank_mapping_check", {})
    if check:
        worst = max(abs(v - 1) for v in check.values())
        out += [
            "",
            f"Table des rangs vérifiée sur les gagnants européens : écart maximal "
            f"{_f(worst * 100, 1)} % entre gagnants observés et probabilités exactes.",
        ]
    return [*out, ""]


def popularity_section(d3: list[dict[str, Any]]) -> list[str]:
    if not d3:
        return []
    out = [
        "## 8. Popularité des numéros et gains (D3, exploratoire)",
        "",
        "Variation du rapport par gagnant pour chaque boule <= 31 en plus dans le tirage "
        "(ère 2016-09). Le tirage étant aléatoire, c'est quasiment une expérience randomisée.",
        "",
        "| Rang | Tirages | Variation par boule <= 31 | p | Spearman |",
        "|---|---|---|---|---|",
    ]
    for r in d3:
        out.append(
            f"| {r['test_id'].split('rank')[-1]} | {r['n_draws']} | {_pct(r['observed'], 1)} | "
            f"{_p(r['p_value'])} | {_f(r['detail']['spearman_rho'], 2)} |"
        )
    out += [
        "",
        "Lecture : les joueurs surjouent les petits numéros (dates de naissance). Quand ils "
        "sortent, les gagnants sont plus nombreux et chacun touche moins. Cela ne change pas "
        "la probabilité de gagner, seulement le montant quand on gagne.",
        "",
    ]
    return out


def forward_section(summary: dict[str, Any] | None, pending: list[dict[str, Any]]) -> list[str]:
    out = ["## 9. Carnet à terme : les tirages à venir (F1, R1)", ""]
    logics = (summary or {}).get("logics", {})
    if logics:
        out += [
            "| Logique | Tirages | Boules trouvées | z | Étoiles | Gains | Rendement |",
            "|---|---|---|---|---|---|---|",
        ]
        for name, s in logics.items():
            out.append(
                f"| {LABELS.get(name, name)} | {s['draws']} | {_f(s['mean_balls'])} | "
                f"{_z(s['z_balls'])} | {_f(s['mean_stars'])} | {_f(s['paid_eur'], 2)} EUR | "
                f"{_pct(s['roi'])} |"
            )
        out.append("")
    else:
        out += ["Aucun tirage noté pour l'instant.", ""]
    if pending:
        out += [
            "Grilles figées en attente du tirage :",
            "",
            "| Tirage | Logique | Grille |",
            "|---|---|---|",
        ]
        for g in pending:
            grid = (
                " ".join(f"{b:02d}" for b in g["balls"])
                + " ★ "
                + " ".join(f"{s:02d}" for s in g["stars"])
            )
            out.append(f"| {g['draw_date']} | {LABELS.get(g['logic'], g['logic'])} | {grid} |")
        out.append("")
    out += [
        "Ce qu'il faudra pour conclure : une logique qui trouverait +0,1 boule par tirage "
        "demande environ 325 tirages (3 ans) pour être vue ; +0,15 environ 145 tirages.",
        "",
    ]
    return out


def render(
    analysis: dict[str, Any],
    control: dict[str, Any] | None,
    backtest: dict[str, Any] | None,
    forward: dict[str, Any] | None,
    pending: list[dict[str, Any]],
) -> str:
    results = analysis["results"]
    summary = analysis["summary"]
    total = sum(v["tests"] for v in summary.values())
    nominal = sum(v["nominal_p_lt_0_05"] for v in summary.values())
    survivors = sum(v["bh_survivors"] for v in summary.values())
    lines = [
        "# EuroMillions — que disent 22 ans de tirages ?",
        "",
        f"Données : {_n(analysis['n_draws'])} tirages officiels FDJ, du {analysis['first_draw']} au "
        f"{analysis['last_draw']}. Analyse du {analysis['created_at'][:10]}. Toutes les "
        "hypothèses ont été inscrites au registre chaîné avant le calcul (`em-A1` à `em-R2`).",
        "",
        "**En bref.** "
        f"{nominal} tests sur {total} sortent à p < 0,05, soit à peu près ce que le hasard seul "
        f"produit ({_f(0.05 * total, 1)}). "
        + ("Aucun ne survit" if survivors == 0 else f"{survivors} survivent")
        + " à la correction pour tests multiples."
        " Les numéros chauds, froids, en retard ou répétés ne sortent ni plus ni moins "
        "que les autres, et aucune logique ne bat un joueur au hasard. Le seul effet net ne "
        "porte pas sur le tirage mais sur les joueurs : les petits numéros, surjoués, "
        "rapportent moins quand ils sortent.",
        "",
    ]
    lines += power_section()
    lines += control_section(control)
    lines += mechanism_section(results, summary)
    lines += theories_section(results)
    lines += shape_section(results)
    lines += backtest_section(backtest)
    lines += payout_section(backtest)
    lines += popularity_section(analysis.get("d3_popularity", []))
    lines += forward_section(forward, pending)
    lines += [
        "## 10. Conclusion",
        "",
        "Sur l'historique, le tirage EuroMillions se comporte comme un hasard équitable et sans "
        "mémoire, à la précision que 1 987 tirages permettent : un biais de 19 % sur une boule "
        "désignée d'avance (28 % sur n'importe laquelle des 50), ou un effet chaud / froid / "
        "retard de 5 à 10 %, aurait été vu 8 fois sur 10. Rien de tel. Le juge définitif reste le carnet à terme, qui fait jouer chaque "
        "logique et le témoin hasard sur tous les tirages à venir.",
        "",
        "*Rapport régénéré par `predlab lottery report` à partir de `data/lottery/*.json`.*",
        "",
    ]
    return "\n".join(lines)
