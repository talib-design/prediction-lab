# Méthodologie

Règles fixées **avant** le premier modèle. Elles peuvent être révisées, mais toute
révision est datée ici et vaut seulement pour les évaluations lancées après elle.

Héritage de la phase loterie (archivée) : la puissance avant les résultats, les règles
de score propres, le refus d'une conclusion que l'échantillon ne permet pas, et
INCONCLUSIVE ≠ REJECTED. La loterie a montré qu'un banc d'essai honnête sait dire
« rien trouvé » ; les courses vont tester s'il sait aussi dire « quelque chose ».

## 1. La question

> Peut-on estimer l'issue d'une course de plat en France mieux que des baselines
> simples et que le marché, avec seulement l'information disponible avant le départ ?

## 2. Unité, sortie, score

- **Unité d'évaluation : la course.** Chaque modèle produit une probabilité de victoire
  par partant, qui somme à 1 sur la course (`core/probability.py`).
- **Score principal : log loss de la course** = −log p(gagnant), après renormalisation
  sur les partants effectifs (un non-partant retiré après la prédiction ne pénalise
  personne ; la prédiction d'origine reste au registre).
- **Dead-heat** (ex-aequo pour la 1re place) : moyenne des −log p des co-gagnants.
- **Scores secondaires, diagnostiques :** Brier multi-classe, erreur de calibration
  par tranche de probabilité, courbe de fiabilité, top-1, rappel top-3, rang du
  gagnant. Aucun d'eux ne décide seul : le taux de gagnant trouvé est explicitement
  exclu comme critère (il récompense les favoris, pas la qualité des probabilités).
- Probabilités écrêtées à `[1e-6, 1 − 1e-6]` ; la borne est rapportée avec chaque
  résultat parce qu'elle flatte légèrement les modèles trop confiants.

## 3. L'information disponible — la règle qui prime sur toutes les autres

- Chaque fait porte `known_at`. Un modèle qui prédit à l'instant *t* ne voit que les
  faits avec `known_at < t`. Ce n'est pas une convention : la vue remise au modèle ne
  contient pas le reste (principe du `HistoryView` de la phase loterie, repris en
  Phase 3 sous le nom `PointInTimeView`).
- Pour les données rétro-chargées, `known_at` est prudent : le résultat d'une course
  est réputé connu **le lendemain** en v1.
- **Cotes :** une cote n'est utilisable que si son horodatage `reported_at` est
  antérieur à l'instant de prédiction. Constat vérifié le 2026-09-28 : la « dernière
  cote directe » archivée par le PMU est horodatée **après** le départ programmé. Elle
  sert d'étalon (marché de clôture), jamais d'entrée d'un modèle.
- **Météo :** une prévision avec son heure d'émission, jamais l'observation.

## 4. Baselines (obligatoires avant tout modèle)

| # | Baseline | Rôle |
|---|---|---|
| 1 | Aléatoire | contrôle du banc : doit scorer comme 2 |
| 2 | Uniforme (1/n partants) | plancher |
| 3 | Taux de victoire historique, rétréci (Bayes empirique) | le passé brut |
| 4 | Forme simple (places récentes, repos) | le bon sens du turfiste |
| 5a | Marché brut : (1/cote) / Σ(1/cote), au même horizon | l'information du public |
| 5b | Marché calibré : 5a corrigé du biais favori–outsider, ajusté sur le train | **la barre à battre** |

## 5. Critère de réussite (pré-enregistré, ajustable)

Trois niveaux, dans l'ordre. Un niveau n'est revendiqué que si le précédent l'est.

1. **Le banc fonctionne :** sur des courses synthétiques à vérité connue, un avantage
   planté est trouvé, un biais de marché planté est corrigé, et un faux avantage
   (marché + bruit) est refusé — `predlab racing synthetic-check`, 10 000 courses.
   **Atteint le 2026-09-28** (3 graines sur 3).
2. **Mieux que les baselines non-marché :** log loss hors échantillon inférieure à
   celle des baselines 1 à 4.
3. **Mieux que le marché calibré (objectif principal) :** un modèle qui *combine* le
   marché et des variables fondamentales (approche Bolton & Chapman 1986, Benter 1994)
   fait mieux que 5b au même horizon, sur la fenêtre de test :
   - différence de log loss appariée course par course ;
   - intervalle bootstrap à 95 % par blocs de courses consécutives qui exclut 0 ;
   - test de permutation apparié par blocs, p < 0,05 **après** correction
     Benjamini–Yekutieli sur tous les challengers évalués sur cette fenêtre ;
   - taille d'échantillon au moins égale à celle que l'analyse de puissance (Phase 3)
     exige pour détecter Δ = 0,01 avec 80 % de puissance. En dessous : INCONCLUSIVE,
     quel que soit le signe.
4. **Confirmation en conditions réelles :** les prédictions enregistrées avant le
   départ, sur des courses futures, reproduisent le signe de l'écart.

Ce critère est volontairement exigeant ; il sera ajusté après les premiers backtests,
et l'ajustement sera daté ici.

## 6. Découpage et usage de la fenêtre de test

Chronologique uniquement (`backtest/splits.py`). **Pré-enregistré le 2026-09-28**
(`racing/backtest.py`, `PREREGISTERED_SPLIT`) :

| Phase | Courses dont le jour est… |
|---|---|
| train | ≤ 2022-12-31 |
| validation | 2023-01-01 → 2023-12-31 |
| test | ≥ 2024-01-01 (≈ 2,7 ans, ~11 000 courses attendues) |

Les paramètres libres se choisissent sur la validation. La fenêtre de test se regarde
une fois par hypothèse pré-enregistrée dans le registre (`predlab hypothesis add`).
Les baselines n'ont aucun paramètre choisi sur les données : leurs valeurs sont fixées
dans `racing/models.py`. Le seul paramètre ajusté, l'exposant du marché calibré, est
réajusté tous les 500 résultats publiés, sur les seuls résultats publiés.

## 6 bis. Horizon et éligibilité (v1)

- **Horizon : T-25 min** avant le départ programmé. Choisi pour inclure la cote
  REFERENCE (médiane −30 min depuis 2017, audit) ; toute cote horodatée après
  l'instant de prédiction est exclue au chargement.
- **Course évaluée** si chaque partant a une cote avant l'horizon : tous les modèles,
  marché compris, sont jugés sur exactement les mêmes courses.
- **Partants** = chevaux ayant couru. Un retrait postérieur à l'horizon est ignoré
  (limite connue, faible).

## 7. Champion / challengers

- Le champion est figé (version du modèle + version des features + run qui l'a
  qualifié).
- Un challenger est promu seulement s'il satisfait le niveau 3 sur une fenêtre qu'il
  n'a jamais vue, avec l'échantillon minimal. Pas de promotion sur une série courte,
  pas de ré-entraînement automatique après chaque course.
- L'ampleur d'un gain annoncé est corrigée de la malédiction du vainqueur : le meilleur
  de plusieurs challengers surestime son propre avantage.

## 8. Tests multiples

Toute idée testée entre au registre d'hypothèses, y compris celles qui échouent. Le
nombre de comparaisons faites sur une fenêtre fixe la correction appliquée.

## 9. Simulation de paris fictifs (ajoutée le 2026-09-28)

Même esprit que l'expérience Loto : **aucune mise réelle, aucun compte, aucun pari
passé**. Des tickets imaginaires, réglés avec les rapports officiels du PMU
(`predlab racing simulate`, `racing/betting.py`). Règles fixées avant la première
simulation :

- **Décision** à l'horizon (T-25 min), avec la seule carte de course ; **paiement** au
  rapport final. Le glissement des cotes entre les deux fait partie de la mesure.
- **Une unité par ticket** : 1 € (simple, tiercé), 2 € (mise de base du Quinté+).
  Aucun plan de mise, aucune gestion de capital.
- **Stratégies** : pour chaque famille, un témoin *favori* et un témoin *hasard* sur
  les mêmes courses ; `top <modèle>` (le plus probable), `valeur <modèle>`
  (p × cote ≥ **1,10**, seuil fixé ici), tiercé et quinté dans l'ordre le plus probable
  (modèle d'ordre de Harville), sur les courses à Quinté+ seulement.
- **Verdict** sur la phase de test : ROI avec IC 95 % par bootstrap en blocs ;
  « gain significatif » seulement si l'IC entier est au-dessus de 0. La part du plus
  gros gain est publiée : un ROI porté par un coup n'est pas un résultat.
- **Critère de réussite financier** (en plus du §5) : une stratégie à gain significatif
  sur le test, **puis** confirmée sur des courses futures enregistrées avant le départ.
  Résultat attendu, dit à l'avance : une perte pour toutes, le prélèvement étant retenu
  avant redistribution. La vraie question est « un modèle perd-il significativement
  moins que les témoins ? ».

## Révisions

- 2026-09-28 — version initiale (passage de la loterie aux courses).
- 2026-09-28 — découpage pré-enregistré, horizon T-25 min, règle d'éligibilité, niveau 1 atteint.
- 2026-09-28 — §9 : simulation de paris fictifs (simple, tiercé, quinté), règles fixées avant tout résultat.
- 2026-09-28 — trot attelé et trot monté ajoutés (décision de Chris). Chaque discipline est
  évaluée **séparément** (backtest, simulation, calibration du marché, découpage identique) ;
  aucun résultat d'une discipline ne vaut pour une autre. Au trot, la question du §1 se
  lit « course de trot » ; la réduction kilométrique d'une course est un résultat, jamais une entrée.
