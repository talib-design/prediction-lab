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
   planté est trouvé et un faux avantage (fort en échantillon, nul hors échantillon)
   est refusé.
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

Chronologique uniquement (`backtest/splits.py`). Les paramètres libres se choisissent
sur la validation. La fenêtre de test se regarde une fois par hypothèse
pré-enregistrée dans le registre (`predlab hypothesis add`).

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

## Révisions

- 2026-09-28 — version initiale (passage de la loterie aux courses).
