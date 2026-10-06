# Modèle Marché+ — trot attelé

Généré le 2026-10-06T07:42:42+00:00 · courses : apprentissage 2012, réglage 2064, test 7213 · λ = 1000 · α du marché seul = 1.135.

## Ce que chaque facteur ajoute à la cote (fenêtre d'apprentissage)

Effet = chances de gagner multipliées par ce nombre pour un écart-type de plus du facteur, *à cote égale*. ×1,00 : la cote l'avait déjà intégré.

| Facteur | β | IC 95 % | Effet par écart-type | p |
|---|---:|---|---:|---:|
| Cote (marché) | 1.130 | [1.076 ; 1.185] | — | 0.000 |
| Forme : places gagnées sur la cote, courses passées | -0.042 | [-0.083 ; -0.001] | ×0.959 | 0.047 |
| Préférence du cheval pour ce terrain | 0.018 | [-0.019 ; 0.056] | ×1.019 | 0.335 |
| Préférence du cheval pour cette température | -0.010 | [-0.050 ; 0.031] | ×0.990 | 0.644 |
| Aucune course connue depuis 2024 | 0.019 | [-0.031 ; 0.068] | ×1.019 | 0.463 |
| Repos (log des jours depuis la dernière course) | -0.014 | [-0.063 ; 0.036] | ×0.987 | 0.592 |
| Jockey / driver : victoires vs cote | 0.006 | [-0.034 ; 0.045] | ×1.006 | 0.783 |
| Entraîneur : victoires vs cote | 0.016 | [-0.024 ; 0.055] | ×1.016 | 0.434 |
| Position au départ (0 = intérieur, 1 = extérieur) | -0.013 | [-0.052 ; 0.026] | ×0.987 | 0.521 |
| Position au départ, sprints du plat | — | inactif (aucune variation) | — | — |
| Poids porté vs moyenne de la course (kg) | — | inactif (aucune variation) | — | — |
| Recul au trot (par 25 m) | -0.043 | [-0.087 ; 0.002] | ×0.958 | 0.061 |

## Réglage : log loss par course (plus bas = mieux)

Modèle 2.0185 · marché calibré 2.0195 · différence -0.0010 [-0.0041 ; 0.0021] sur 2064 courses → **pas de différence démontrée**.

## Test (décision) : log loss par course (plus bas = mieux)

Modèle 1.9758 · marché calibré 1.9750 · différence 0.0008 [-0.0010 ; 0.0027] sur 7213 courses → **pas de différence démontrée**.

## Test : paris fictifs à 1 €

| Stratégie | Paris | ROI | IC 95 % | Taux de réussite |
|---|---:|---:|---|---:|
| SG modèle | 7213 | -11.1 % | [-14.2 % ; -7.7 %] | 32.9 % |
| SG favori | 7213 | -11.4 % | [-14.5 % ; -8.2 %] | 32.9 % |
| SP modèle | 7213 | -7.4 % | [-9.2 % ; -5.6 %] | 58.7 % |
| SP favori | 7213 | -6.8 % | [-8.5 % ; -5.0 %] | 59.1 % |
| SG valeur modèle | 199 | -50.4 % | [-70.6 % ; -25.9 %] | 10.1 % |
