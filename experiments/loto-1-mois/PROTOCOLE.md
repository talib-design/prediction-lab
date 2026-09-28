# Protocole — Expérience « Loto, 1 mois »

Fixé le 26 septembre 2026, **avant** la première prédiction. Rien de ce qui suit ne
change en cours de route. Seuls les deux paramètres de la grille adaptative bougent,
et uniquement par la règle décrite ci-dessous.

## Question

Une grille qui « apprend » de chaque tirage fait-elle mieux, sur un mois, qu'une
grille tirée au hasard ?

Réponse attendue d'après le Milestone 1 (875 tirages évalués) : non. L'expérience
sert à le vérifier en conditions réelles, sur des tirages futurs, avec une boucle
automatisée de bout en bout.

## Période

Du tirage du **samedi 26/09/2026** à celui du **lundi 26/10/2026** inclus. Ce sont les
tirages réguliers du lundi, du mercredi et du samedi, soit 14 tirages. Les tirages
spéciaux (Super Loto, Grand Loto) sont exclus.

## Les trois grilles, à chaque tirage

| Grille | Règle | Rôle |
|---|---|---|
| `adaptatif` | Fréquence pondérée dans le temps (demi-vie *h* tirages). En mode `chaud`, on joue les numéros les plus sortis ; en mode `froid`, les moins sortis. | Celle qui apprend |
| `frequence` | Fréquence sur tout l'historique, top 5. Jamais modifiée. | Modèle du Milestone 1 |
| `hasard` | 5 numéros + chance au hasard, graine = SHA-256 de la date du tirage | Témoin |

## Règle d'apprentissage (après chaque tirage)

Les 12 réglages possibles (*h* ∈ {10, 25, 50, 100, 300, ∞} × {chaud, froid}) sont
rejoués sur les **30 derniers tirages**, en walk-forward. On garde celui qui a
trouvé le plus de bons numéros ; en cas d'égalité, celui qui a la meilleure « masse »
de probabilité. C'est automatique et reproductible (`cycle.py learn`).

L'analyse écrite (dans `journal.md`) commente cet apprentissage. Elle ne peut pas le
modifier à la main.

## Mesures

- Par grille et par tirage : nombre de bons numéros (attendu au hasard : 0,51),
  numéro chance trouvé (attendu : 1 fois sur 10), rang FDJ atteint.
- Cumulé : total de bons numéros par grille, avec une p-valeur exacte (loi
  hypergéométrique) donnant la probabilité d'obtenir au moins ce total au hasard.

## Règle de décision, fixée d'avance

On ne conclut qu'une grille « fait mieux que le hasard » que si sa p-valeur
cumulée finale est **< 0,05 après correction de Bonferroni sur 3 grilles**,
c'est-à-dire < 0,0167.

Avertissement de puissance : sur 14 tirages, une grille au hasard trouve en moyenne
7,1 bons numéros, avec un écart-type de 2,4. Pour passer le seuil, il en faudrait
au moins 14, soit le double. Un vrai avantage de quelques pour cent est donc
**indétectable** en un mois. Un résultat nul ne prouvera pas que le Loto est
équitable ; il montrera seulement que la mesure ne pouvait pas voir mieux.

## Intégrité

- `journal.jsonl` est en ajout seul et chaîné par hachage (`cycle.py verify`).
- Une prédiction est refusée si son tirage, ou un tirage plus récent, est déjà
  connu. Elle ne peut jamais être réécrite.
- Chaque résultat officiel exige deux sources distinctes, dont fdj.fr.
- L'horodatage externe vient de la session Claude qui publie chaque prédiction
  avant le tirage. Un commit git poussé sur GitHub le renforcerait.

Ceci est une expérience de mesure, pas un conseil de jeu.

## Amendement du 26/09/2026, 18h (avant tout résultat noté)

Constat : un cycle lancé le 26/09 à 17h52, avant le tirage, aurait pu enregistrer la
prédiction du 28/09 sans connaître le résultat du 26/09. Comme une prédiction est
immuable, la grille adaptative aurait sauté une étape d'apprentissage.

Règle ajoutée, appliquée par `cycle.py predict` (et visible avec `cycle.py next`) :

- on ne prédit un tirage que si le tirage régulier **qui le précède** est déjà
  enregistré dans `historique.csv` (le tirage du jour compte comme précédent) ;
- `learn` doit avoir tourné après ce tirage ;
- la cible ne peut pas être passée, ni être le tirage du jour après 20h00 (Paris).

Si un résultat n'est pas disponible à temps, le tirage suivant reste sans prédiction.
Il est signalé comme tel, pas rattrapé. Un passage de rattrapage a lieu le lendemain
matin de chaque tirage pour limiter ce cas.

Rien ne change dans les grilles, la règle d'apprentissage, les mesures ni la règle de décision.

## Amendement du 26/09/2026, 18h30 : simulation financière (avant tout résultat noté)

Chaque grille est jouée **fictivement** à 2,20 €, le prix d'une grille simple Loto
(source : fdj.fr, « Comment jouer »). Le 2nd tirage, en option à 0,80 €, n'est pas joué.

- Après chaque tirage, on enregistre les rapports officiels du 1er tirage, rangs 1 à 9,
  lus sur deux sources distinctes (loto-stats.fr et lesbonsnumeros.com, ou fdj.fr) :
  `cycle.py add-rapports DATE r1 … r9 --source … --source2 …`, avec « - » pour un rang
  sans gagnant.
- Le gain d'une grille est le rapport officiel du rang qu'elle atteint. `BILAN.md`
  affiche la mise, les gains, le net et le taux de retour de chaque grille. Il les compare
  à l'espérance exacte d'une grille au hasard, calculée avec les rapports réels de chaque
  tirage.
- Les codes LOTO (tirage au sort à 20 000 €) ne sont pas simulables et sont exclus.
- Si une grille atteint un rang sans autre gagnant (jackpot), son gain est « non
  déterminable ». Il est signalé et traité à part dans le rapport final.

C'est une mesure secondaire. Elle ne change pas la règle de décision, qui porte
sur les bons numéros. Sur 14 tirages, le résultat financier est dominé par la chance :
un seul 3 bons numéros (≈ 17 à 47 €) suffit à inverser le classement.
