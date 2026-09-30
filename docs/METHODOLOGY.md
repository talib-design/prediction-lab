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

Chronologique uniquement (`backtest/splits.py`). **Pré-enregistré le 2026-09-28, révisé
le 2026-09-30** quand l'historique a été limité à 2024 (`racing/backtest.py`,
`PREREGISTERED_SPLIT`) — avant qu'aucun modèle challenger n'ait été évalué :

| Phase | Courses dont le jour est… |
|---|---|
| train | 2024-01-01 → 2024-06-30 |
| validation | 2024-07-01 → 2024-12-31 |
| test | ≥ 2025-01-01 (≈ 21 mois au 2026-09, ~7 500 courses de plat, un peu plus chaque mois) |

Conséquence assumée : la fenêtre de test est au départ un peu sous l'estimation de
~8 000 courses pour détecter Δ = 0,01 ; elle la dépasse avec le temps, et le carnet
(§9 bis) ajoute des courses réellement futures.

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
- **Marché cohérent** (ajouté le 2026-09-29, après la première simulation) : aucun ticket
  sur une course dont les cotes à l'horizon ne forment pas un marché, c.-à-d.
  Σ 1/cote hors de [1,05 ; 1,60]. Un pool PMU formé est vers 1,19 ; sous 1,05 les cotes
  sont d'un pool encore vide et tous les chevaux paraissent « valeur » (1,4 % des courses
  de plat 2025-2026 à T-25). Constaté sur « SG valeur marché calibré » : 11 tickets par
  course sur 28 courses. La règle vaut aussi pour le carnet (§9 bis).
- **Critère de réussite financier** (en plus du §5) : une stratégie à gain significatif
  sur le test, **puis** confirmée sur des courses futures enregistrées avant le départ.
  Résultat attendu, dit à l'avance : une perte pour toutes, le prélèvement étant retenu
  avant redistribution. La vraie question est « un modèle perd-il significativement
  moins que les témoins ? ».

## 9 bis. Carnet de paris fictifs en direct (ajouté le 2026-09-28)

Le niveau 4 du §5 : des décisions écrites **avant** la course.

- À chaque passe du collecteur (5 min), toute course cible entrée dans sa fenêtre
  [départ − 25 min, départ[ est **figée** : tickets de chaque stratégie, calculés avec
  les seules cotes horodatées avant T-25 (même règle que le backtest), écrits dans
  `data/carnet.jsonl`, registre chaîné par hash.
- Une course non figée avant son départ (Mac en veille, marché incomplet) n'est
  **jamais rattrapée** : l'absence est la trace honnête.
- **Règlement** au rapport officiel, dès qu'il est collecté. Simple sur un non-partant :
  remboursé. Tiercé/quinté avec un non-partant : réglé tel quel, signalé (approximation).
- Stratégies v1 : SG favori / hasard / valeur (marché calibré), SP favori / hasard,
  tiercé et quinté favoris / hasard (Quinté+ seulement). α du marché calibré : dernier
  backtest de la discipline, sinon 1 (marché brut), noté dans chaque enregistrement.
- Le carnet ne contient que nos décisions et probabilités, pas les cotes PMU (référencées
  par le hash des captures). Le commiter dans git lui donne une date publique.

## 10. Profil des vainqueurs et modèle Marché+ (ajouté le 2026-09-30)

Demande de Chris : regarder comment le terrain, la météo, la position au départ… pèsent
sur la cote et sur le classement, cheval par cheval, puis prévoir.

**Une seule table** (`racing/features.py`) : une ligne par partant, marché à T-25 min,
courses au marché complet et cohérent (§9), depuis le 2024-01-01. Le passé d'un cheval,
d'un jockey, d'un entraîneur est lu par une jointure « à date » qui **exclut le jour de la
course** : même règle que `result_known_at`, même code pour 2024 et pour la course de
tout à l'heure (un test vérifie l'égalité des deux chemins).

**Profil des vainqueurs (descriptif)** — `racing/profile.py`. Niveaux fixés le 2026-09-30
avant tout résultat (`LEVELS`).

- *Conditions de course* (terrain, température, ciel, vent, distance, peloton) : il y a un
  gagnant par course, donc une condition ne fait pas « gagner plus ». On mesure si le
  favori gagne plus ou moins que sa cote, la cote médiane du gagnant, la part de gagnants
  hors des trois premières cotes.
- *Profil des partants* (position au départ, repos, âge, sexe, poids, recul, ferrure,
  rang de cote) : victoires / hasard (Σ 1/partants), cote / hasard, **victoires / cote**
  (ce que la cote a raté) et top 3 / top 3 attendu par la cote (Harville).
- Pas de « places gagnées sur la cote » : un favori ne peut que perdre des places et un
  outsider qu'en gagner, quel que soit le facteur. Mesure écartée le 2026-09-30.
- IC 95 % par approximation normale d'une somme de Bernoulli ; pas d'intervalle sous
  5 victoires attendues ; verdicts ▲ / ▼ après Benjamini-Yekutieli à 5 % sur tous les
  tests affichés ; stabilité 2024 contre 2025-2026.
- Le profil couvre toute la période, fenêtre de test comprise : il décrit, il ne choisit
  rien. Aucune entrée du modèle n'a été choisie en le regardant.
- Par cheval, dans les conditions d'une course : courses, top 3 et top 3 attendu par la
  cote, ici et ailleurs ; ▲ / ▼ seulement avec au moins 3 courses de chaque côté et un
  écart d'un quart de top 3 par course. Indicatif.

**Marché+ v1** — `racing/marketplus.py`. Logit conditionnel :
score = α·log q + Σ βₖ·xₖ, probabilités normalisées par course. Avec β = 0, c'est le marché
calibré : chaque β se lit « à cote égale ».

- Entrées (`MODEL_FEATURES`), figées dans le code avant la première exécution : forme
  (places gagnées sur la cote, rétrécie k = 2), préférence du cheval pour le terrain et
  pour la température du jour (k = 3), aucune course connue, log du repos, jockey et
  entraîneur (victoires / cote, k = 3), position au départ, position au départ en sprint
  (plat < 1 400 m), poids vs moyenne de la course, recul au trot.
- Procédure : Newton exact, pénalité ridge λ ∈ {1, 10, 100, 1000} sur les β seuls, λ
  choisi sur la validation, référence = marché calibré ajusté sur le même apprentissage.
  Paramètres du carnet : même λ, réajusté chaque nuit sur tout l'historique publié.
- **Première lecture du test, plat, 2026-09-30 à 07:34 UTC** (6 257 courses depuis 2025) :
  log loss −0,0037 par course contre le marché calibré, IC 95 % [−0,0056 ; −0,0018] →
  meilleur que le marché. Aucun facteur n'est significatif seul ; l'amélioration est
  petite. Paris fictifs à 1 € sur le test : SG modèle −12,5 % contre SG favori −13,0 %,
  SP modèle −10,4 % contre −11,5 % : **pas de gain exploitable**, la marge du PMU reste
  hors de portée. λ retenu = 1000, à la borne de la grille. Toute v2 passe par la
  validation puis une nouvelle lecture enregistrée du test.
- Carnet : témoins « SG modèle », « SP modèle » et « SG valeur (modèle) » ajoutés le
  2026-09-30 avant leur premier ticket, figés à T-25 avec les probabilités du modèle.
  Si le modèle échoue (base en reconstruction), les autres tickets sont figés quand même
  et l'erreur est écrite dans le carnet.
- Limites : historique depuis 2024 seulement (« aucune course connue » mêle débutants et
  chevaux plus anciens) ; au trot le terrain n'est pas mesuré ; pas de modèle tant que
  l'apprentissage compte moins de 300 courses.

## 11. Banc d'essai des stratégies (ajouté le 2026-09-30)

Demande de Chris : parier fictivement, sans limite, sur toutes les courses à venir avec
des stratégies construites sur les apprentissages, pour trouver une combinaison de
critères qui rapporte plus qu'elle ne mise (objectif : +10 %). `racing/strategies.py`.

- **Stratégie** = des critères (1 à 3) + un pari (simple gagnant ou simple placé) +
  1 € par ticket, sur chaque partant qui remplit les critères. Aucun plan de mise, aucune
  martingale, aucun pari réel.
- **Critères** (`DIMENSIONS`) : ceux du profil (§10) et de nouveaux, tous connus avant la
  course — tranche de cote, classement et « valeur » de Marché+ (p × cote), type de
  course, hippodrome, dernière course et régularité lues dans la musique (vérifiée le
  2026-09-28 : elle n'inclut pas la course elle-même), distance, niveau (allocation) et
  oeillères comparés à la dernière course, changement de jockey annoncé, réussite du
  jockey, de l'entraîneur et du duo (victoires / cote, passé seulement), réussite du
  cheval sur ce terrain. Les niveaux « inconnu » ne sont jamais un critère.
- **Marché+ comme critère** : pour l'historique, chaque mois est prédit par un modèle
  ajusté sur les mois précédents seulement (λ du dernier rapport).
- **Recherche stricte (jauge)** : explorée sur 2024 (gardée si positive dans chaque
  moitié de la période), confirmée une fois sur 2025-2026 (test unilatéral « retour > 0 »,
  Benjamini-Yekutieli). Les confirmées entrent au banc.
  **Première mesure, 2026-09-30, plat : 0 sur 200.** Les 200 meilleures combinaisons de
  2024 y rapportaient +18 % en moyenne ; sur 2025-2026, −16 %. Leçon : ce qui « marche »
  une année est d'abord de la chance.
- **Recherche « chaque année »** : explorée sur tout l'historique, gardée seulement si
  elle est positive séparément en 2024, en 2025 et en 2026 (au moins 40 paris par année,
  200 au total). Aucune fenêtre ne reste pour la confirmer : ce sont les courses à venir
  qui jugent. Les 100 meilleures par type de pari (borne basse de l'IC) entrent au banc.
- **Références** : simple gagnant et simple placé sur le favori.
- **En direct** : chaque stratégie non éliminée joue chaque course cible, figée à T-25
  comme le carnet, dans son propre registre chaîné `data/banc/ledger.jsonl`, avec son
  propre bilan (jamais mélangé au carnet). Un non-partant est remboursé.
- **Verdicts, sur les seuls paris en direct** : *gagnante* à partir de 300 paris si la
  borne basse de l'IC 95 % du retour est au-dessus de 0 ; *éliminée* (définitivement) à
  partir de 100 paris si la borne haute est sous −5 % ; *en test* sinon. Rien n'est
  effacé ; l'historique du banc est dans git.
- Limite assumée : les critères précis se présentent rarement (5 à 6 tickets par course
  de plat au lancement) ; conclure prendra des semaines, davantage pour les stratégies
  les plus rares.

## Révisions

- 2026-09-28 — version initiale (passage de la loterie aux courses).
- 2026-09-28 — découpage pré-enregistré, horizon T-25 min, règle d'éligibilité, niveau 1 atteint.
- 2026-09-28 — §9 : simulation de paris fictifs (simple, tiercé, quinté), règles fixées avant tout résultat.
- 2026-09-29 — §9 : règle du marché cohérent ; le backtest (log loss) n'est pas modifié.
- 2026-09-28 — historique limité à 2023 (décision de Chris : chevaux encore en activité) ;
  découpage révisé en conséquence (train 2023, validation 2024, test ≥ 2025), avant tout
  challenger. §9 bis : carnet en direct.
- 2026-09-30 — §11 : banc d'essai des stratégies ; jauge stricte 0/200 sur le plat.
- 2026-09-30 — §10 : profil des vainqueurs et modèle Marché+ v1, entrées pré-enregistrées,
  première lecture du test datée ; trois témoins « modèle » au carnet.
- 2026-09-30 — historique limité à 2024 (décision de Chris : rien de plus ancien n'est utile).
  Découpage révisé, avant tout challenger : train 1er semestre 2024, validation 2e semestre
  2024, test ≥ 2025 inchangé (la fenêtre de test garde sa taille). Les premières semaines
  de 2024 ont un historique de forme court : les variables de forme y sont moins informées.
- 2026-09-28 — trot attelé et trot monté ajoutés (décision de Chris). Chaque discipline est
  évaluée **séparément** (backtest, simulation, calibration du marché, découpage identique) ;
  aucun résultat d'une discipline ne vaut pour une autre. Au trot, la question du §1 se
  lit « course de trot » ; la réduction kilométrique d'une course est un résultat, jamais une entrée.
