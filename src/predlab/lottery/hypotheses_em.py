"""Pre-registration of every EuroMillions hypothesis, written before any result is computed.

The point of this file is its timestamp: each theory below, with the statistic that will
judge it and the decision rule, is appended to the hash-chained registry *before* the
analysis code is run on the draws. Nothing here may be edited after the fact -- a changed
rule is a new hypothesis with a new id.

Conventions shared by every entry:

* H0 is "the draw mechanism is fair and draws are independent". Under H0 every number has
  inclusion probability k/N in every draw, whatever happened before.
* Multiplicity: Benjamini-Hochberg at q = 0.05, applied **within each sub-family**: A1, A2,
  A3, A4, B (B1 to B4 together, 20 tests), C1, C2, C3. The number of tests at nominal p < 0.05 is also reported next to the number
  expected by chance (0.05 x number of tests), so a lone p = 0.03 cannot pass as a finding.
* Confirmation: a family-B or family-C effect is only called SUPPORTED if it passes BH on
  the whole sample AND has the same sign with p < 0.05 on the later half (draws from
  2020-01-01), AND (family B) survives the forward carnet. Otherwise it is INCONCLUSIVE:
  failing to detect is never written down as "REJECTED", because the detection floor
  (about 19 % relative for one ball, 29 % after correcting for 50 balls, at 1 987 draws)
  says what could not have been seen.
* The forward carnet (draws not yet played at registration time) is the vault.
* Family R (pure chance) is the control: a random player in every comparison (R1) and the
  whole battery rerun on synthetic fair histories (R2), so the lab's own false-positive
  rate is measured, not assumed.
"""

from __future__ import annotations

from predlab.registry.hypotheses import Hypothesis, HypothesisRegistry, Origin

DATASET = "euromillions"

_FOLK = Origin.FOLK_HEURISTIC


def _h(hid: str, description: str, *, origin: Origin = _FOLK, experiment: str) -> Hypothesis:
    return Hypothesis(
        hypothesis_id=hid,
        description=description,
        origin=origin,
        dataset=DATASET,
        experiment=experiment,
    )


EM_HYPOTHESES: tuple[Hypothesis, ...] = (
    _h(
        "em-A1",
        "EuroMillions A1 -- uniformité des boules. Les 50 boules sortent à fréquence égale "
        "(5/50 par tirage). Statistique : chi² de Pearson sur les comptes, p-value par "
        "simulation Monte-Carlo de tirages équitables (20 000), pour les boules de tous les "
        "tirages 2004-2026 et par époque (2004-02, 2011-05, 2016-09). Étoiles : même test par "
        "époque (9, 11, 12 étoiles). 7 tests, BH q=0,05.",
        experiment="analysis-v1/A1",
    ),
    _h(
        "em-A2",
        "EuroMillions A2 -- une boule ou étoile précise est favorisée ou défavorisée. "
        "Test binomial exact bilatéral par numéro (H0 : p = k/N) : 50 boules (tous tirages), "
        "12 étoiles (2016-09), 11 (2011-05), 9 (2004-02) = 82 tests, BH q=0,05. Plancher de "
        "détection annoncé : biais relatif d'environ 19 % sans correction, 29 % avec.",
        experiment="analysis-v1/A2",
    ),
    _h(
        "em-A3",
        "EuroMillions A3 -- ordre d'extraction. La boule extraite en position j (1 à 5) est "
        "uniforme sur 1-50 et de moyenne 25,5. Statistiques : chi² d'uniformité (49 ddl) et "
        "z de la moyenne, pour chacune des 5 positions (10 tests), tous tirages. BH q=0,05.",
        experiment="analysis-v1/A3",
    ),
    _h(
        "em-A4",
        "EuroMillions A4 -- homogénéité. (a) les boules sortent pareil dans les trois époques "
        "(justifie de les regrouper) ; (b) mardi et vendredi donnent les mêmes fréquences "
        "(boules et étoiles, époques 2011-05 et 2016-09). Chi² d'homogénéité, p-value par "
        "permutation des étiquettes (10 000). 5 tests, BH q=0,05.",
        experiment="analysis-v1/A4",
    ),
    _h(
        "em-B1",
        "EuroMillions B1 -- numéros chauds. Les 10 boules les plus sorties sur les W derniers "
        "tirages (W = 20, 50, 100, 300) ressortent plus que 5/50 au tirage suivant. Test "
        "causal exact : à chaque tirage la sélection ne dépend que du passé, donc ses sorties "
        "suivent une loi hypergéométrique sous H0 ; z de la somme des écarts, bilatéral. "
        "Tirages à partir du 301e. Étoiles (ère 2016-09, W = 20, 50, 100) : 3 plus chaudes.",
        experiment="analysis-v1/B1",
    ),
    _h(
        "em-B2",
        "EuroMillions B2 -- numéros froids (« ils vont revenir » ou « ils sont éteints »). "
        "Les 10 boules les moins sorties sur les W derniers tirages (W = 20, 50, 100, 300) "
        "sortent à un taux différent de 5/50. Même test causal que B1, bilatéral. Étoiles "
        "(ère 2016-09) : 3 moins sorties, W = 20, 50, 100.",
        experiment="analysis-v1/B2",
    ),
    _h(
        "em-B3",
        "EuroMillions B3 -- loi des séries. (a) une boule sortie au tirage précédent ressort "
        "plus (ou moins) que 5/50 ; (b) les voisins +-1 des boules du tirage précédent "
        "sortent à un taux différent ; (c) étoiles de l'ère 2016-09 : une étoile sortie "
        "ressort à un taux différent de 2/12. Test causal exact comme B1, bilatéral.",
        experiment="analysis-v1/B3",
    ),
    _h(
        "em-B4",
        "EuroMillions B4 -- retard (« numéro en retard »). (a) les 10 boules au plus long "
        "retard actuel sortent à un taux différent de 5/50 ; (b) les boules en retard d'au "
        "moins 20 tirages idem ; (c) étoiles ère 2016-09 : les 3 étoiles au plus long retard. "
        "Test causal exact comme B1, bilatéral. Sous H0 le retard n'a aucun effet.",
        experiment="analysis-v1/B4",
    ),
    _h(
        "em-C1",
        "EuroMillions C1 -- forme des tirages. La distribution observée de la somme des 5 "
        "boules, du nombre de pairs, du nombre de boules <= 25, du nombre de paires "
        "consécutives, du nombre de dizaines distinctes, du nombre de derniers chiffres "
        "distincts et de l'étendue (max-min) suit la loi exacte obtenue en énumérant les "
        "2 118 760 combinaisons. Chi² d'adéquation sur classes d'effectif attendu >= 5. "
        "Étoiles (2016-09) : somme et paire consécutive. 9 tests, BH q=0,05.",
        experiment="analysis-v1/C1",
    ),
    _h(
        "em-C2",
        "EuroMillions C2 -- combinaisons répétées. Le nombre de paires de tirages avec les "
        "mêmes 5 boules suit une loi de Poisson de moyenne C(n,2)/C(50,5) (environ 0,93 pour "
        "1 987 tirages). Test unilatéral (trop de répétitions) et nombre de combinaisons "
        "distinctes. Un excès signalerait une mécanique non aléatoire ; un déficit rien.",
        experiment="analysis-v1/C2",
    ),
    _h(
        "em-C3",
        "EuroMillions C3 -- indépendance sérielle. La somme des boules d'un tirage n'est pas "
        "corrélée à celle des tirages précédents : autocorrélation de rang 1 et test de "
        "Ljung-Box jusqu'au rang 10, tous tirages. 2 tests, BH q=0,05.",
        experiment="analysis-v1/C3",
    ),
    _h(
        "em-D1",
        "EuroMillions D1 -- une logique de prédiction bat le hasard en marche avant. Logiques "
        "figées à l'avance, sans réglage : fréquence totale, fréquence glissante 100 et 300, "
        "fréquence rétrécie (James-Stein), retard, chaud 50, froid 50, répétition du dernier "
        "tirage. Critère de décision : log loss par numéro contre le tirage uniforme, "
        "bootstrap par blocs et permutation appariée, BH sur les logiques ; critère "
        "secondaire : nombre moyen de numéros trouvés contre la loi hypergéométrique exacte "
        "et contre 1 000 joueurs au hasard. Évaluation marche avant dès le 201e tirage.",
        origin=Origin.HUMAN,
        experiment="backtest-v1/D1",
    ),
    _h(
        "em-D2",
        "EuroMillions D2 -- rendement fictif. Une grille par tirage et par logique (ère "
        "2016-09, 2,50 EUR par grille selon la page FDJ du 2026-10-06), payée au rapport "
        "officiel du rang atteint. Le rendement d'une logique n'est pas distinguable de celui "
        "du hasard si son intervalle (bootstrap par blocs) contient celui du hasard. Rang 1 "
        "traité à part (jackpot non versé = rapport inconnu). Mesure de performance, pas une "
        "stratégie de mise : une seule grille, mise fixe, aucune gestion de bankroll.",
        origin=Origin.HUMAN,
        experiment="backtest-v1/D2",
    ),
    _h(
        "em-D3",
        "EuroMillions D3 -- popularité des numéros et gains (exploratoire, hors prédiction). "
        "Quand beaucoup de boules <= 31 (dates de naissance) sortent, il y a plus de gagnants "
        "dans les rangs intermédiaires et le rapport par gagnant baisse. Régression de "
        "log(rapport du rang r) sur le nombre de boules <= 31, ère 2016-09. Si vrai, cela "
        "ne change pas la probabilité de gagner, seulement le gain espéré quand on gagne.",
        experiment="analysis-v1/D3",
    ),
    _h(
        "em-F1",
        "EuroMillions F1 -- carnet à terme. Pour chaque tirage à venir (mardi, vendredi) une "
        "grille par logique (D1) et une grille hasard sont figées dans un registre chaîné "
        "avant le tirage, puis notées avec les gains officiels. Seul juge définitif : les "
        "tirages futurs. Détectable : une logique qui ajoute +0,1 numéro trouvé par tirage "
        "demande environ 325 tirages (3 ans) ; +0,15 environ 145 tirages (1,4 an).",
        origin=Origin.HUMAN,
        experiment="forward-v1/F1",
    ),
    # Added 2026-10-06 at Chris's request ("un test 100 % hasard"), still before any test
    # had been run on the real draws.
    _h(
        "em-R1",
        "EuroMillions R1 -- joueur témoin 100 % hasard. Une grille tirée au hasard (graine "
        "dérivée de la date du tirage, donc reproductible et non modifiable) joue chaque "
        "tirage du backtest, des gains fictifs et du carnet à terme. C'est la référence : une "
        "logique ne vaut que si elle bat ce témoin. Contrôle de cohérence : sa moyenne de "
        "numéros trouvés doit coller à la loi hypergéométrique (0,5 boule, 2 x 2/12 étoile) ; "
        "un écart |z| > 3 signalerait un bug, pas un talent.",
        origin=Origin.HUMAN,
        experiment="control-v1/R1",
    ),
    _h(
        "em-R2",
        "EuroMillions R2 -- contrôle négatif du labo. Toute la batterie A, B, C est relancée "
        "sur 200 historiques fabriqués 100 % au hasard (même nombre de tirages par époque, "
        "mêmes dates). Pour tenir le temps de calcul : A1 en p asymptotique corrigée, A4 avec "
        "1 000 permutations. Le labo est jugé fiable si (a) la part globale de p < 0,05 est "
        "entre 3 % et 7 %, (b) dans chaque sous-famille au plus 8 % des historiques ont un "
        "survivant BH, (c) les p de la famille B sont uniformes (Kolmogorov-Smirnov p > 0,01). "
        "Sinon les conclusions sur les vrais tirages sont suspendues.",
        origin=Origin.HUMAN,
        experiment="control-v1/R2",
    ),
)


def register_all(registry: HypothesisRegistry) -> list[str]:
    """Append the hypotheses that are not yet in the registry. Returns the new ids."""
    known = {h.hypothesis_id for h in registry.history()}
    added: list[str] = []
    for hypothesis in EM_HYPOTHESES:
        if hypothesis.hypothesis_id in known:
            continue
        registry.add(hypothesis)
        added.append(hypothesis.hypothesis_id)
    return added
