# Modèle Marché+ — plat

Généré le 2026-09-30T07:43:19+00:00 · courses : apprentissage 1509, réglage 1893, test 6257 · λ = 1000 · α du marché seul = 1.055.

## Ce que chaque facteur ajoute à la cote (fenêtre d'apprentissage)

Effet = chances de gagner multipliées par ce nombre pour un écart-type de plus du facteur, *à cote égale*. ×1,00 : la cote l'avait déjà intégré.

| Facteur | β | IC 95 % | Effet par écart-type | p |
|---|---:|---|---:|---:|
| Cote (marché) | 1.057 | [0.975 ; 1.139] | — | 0.000 |
| Forme : places gagnées sur la cote, courses passées | 0.030 | [-0.015 ; 0.075] | ×1.030 | 0.195 |
| Préférence du cheval pour ce terrain | 0.023 | [-0.020 ; 0.066] | ×1.023 | 0.289 |
| Préférence du cheval pour cette température | 0.014 | [-0.030 ; 0.058] | ×1.014 | 0.536 |
| Aucune course connue depuis 2024 | -0.003 | [-0.055 ; 0.049] | ×0.997 | 0.909 |
| Repos (log des jours depuis la dernière course) | -0.011 | [-0.062 ; 0.041] | ×0.989 | 0.688 |
| Jockey / driver : victoires vs cote | 0.019 | [-0.023 ; 0.061] | ×1.019 | 0.377 |
| Entraîneur : victoires vs cote | 0.015 | [-0.027 ; 0.056] | ×1.015 | 0.493 |
| Position au départ (0 = intérieur, 1 = extérieur) | 0.035 | [-0.006 ; 0.076] | ×1.035 | 0.094 |
| Position au départ, sprints du plat | 0.002 | [-0.039 ; 0.042] | ×1.002 | 0.934 |
| Poids porté vs moyenne de la course (kg) | 0.002 | [-0.039 ; 0.044] | ×1.002 | 0.907 |
| Recul au trot (par 25 m) | — | inactif (aucune variation) | — | — |

## Réglage : log loss par course (plus bas = mieux)

Modèle 2.0824 · marché calibré 2.0858 · différence -0.0034 [-0.0065 ; 0.0004] sur 1893 courses → **pas de différence démontrée**.

## Test (décision) : log loss par course (plus bas = mieux)

Modèle 2.0924 · marché calibré 2.0961 · différence -0.0037 [-0.0056 ; -0.0018] sur 6257 courses → **meilleur que le marché**.

## Test : paris fictifs à 1 €

| Stratégie | Paris | ROI | IC 95 % | Taux de réussite |
|---|---:|---:|---|---:|
| SG modèle | 6257 | -12.5 % | [-16.6 % ; -8.5 %] | 27.0 % |
| SG favori | 6257 | -13.0 % | [-17.1 % ; -9.3 %] | 26.8 % |
| SP modèle | 6254 | -10.4 % | [-12.8 % ; -8.3 %] | 56.1 % |
| SP favori | 6254 | -11.5 % | [-13.9 % ; -9.3 %] | 55.8 % |
| SG valeur modèle | 52 | +27.3 % | [-72.1 % ; +125.4 %] | 15.4 % |
