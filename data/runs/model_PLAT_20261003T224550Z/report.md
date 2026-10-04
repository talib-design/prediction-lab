# Modèle Marché+ — plat

Généré le 2026-10-03T22:45:50+00:00 · courses : apprentissage 1751, réglage 1893, test 6299 · λ = 1000 · α du marché seul = 1.082.

## Ce que chaque facteur ajoute à la cote (fenêtre d'apprentissage)

Effet = chances de gagner multipliées par ce nombre pour un écart-type de plus du facteur, *à cote égale*. ×1,00 : la cote l'avait déjà intégré.

| Facteur | β | IC 95 % | Effet par écart-type | p |
|---|---:|---|---:|---:|
| Cote (marché) | 1.084 | [1.008 ; 1.160] | — | 0.000 |
| Forme : places gagnées sur la cote, courses passées | 0.039 | [-0.005 ; 0.083] | ×1.039 | 0.086 |
| Préférence du cheval pour ce terrain | 0.029 | [-0.013 ; 0.071] | ×1.029 | 0.179 |
| Préférence du cheval pour cette température | 0.007 | [-0.036 ; 0.049] | ×1.007 | 0.764 |
| Aucune course connue depuis 2024 | -0.004 | [-0.055 ; 0.047] | ×0.996 | 0.875 |
| Repos (log des jours depuis la dernière course) | -0.001 | [-0.052 ; 0.049] | ×0.999 | 0.956 |
| Jockey / driver : victoires vs cote | 0.015 | [-0.025 ; 0.056] | ×1.015 | 0.466 |
| Entraîneur : victoires vs cote | 0.014 | [-0.025 ; 0.054] | ×1.015 | 0.474 |
| Position au départ (0 = intérieur, 1 = extérieur) | 0.034 | [-0.006 ; 0.073] | ×1.034 | 0.093 |
| Position au départ, sprints du plat | 0.005 | [-0.034 ; 0.043] | ×1.005 | 0.817 |
| Poids porté vs moyenne de la course (kg) | -0.000 | [-0.040 ; 0.040] | ×1.000 | 0.995 |
| Recul au trot (par 25 m) | — | inactif (aucune variation) | — | — |

## Réglage : log loss par course (plus bas = mieux)

Modèle 2.0820 · marché calibré 2.0855 · différence -0.0035 [-0.0068 ; 0.0002] sur 1893 courses → **pas de différence démontrée**.

## Test (décision) : log loss par course (plus bas = mieux)

Modèle 2.0927 · marché calibré 2.0966 · différence -0.0039 [-0.0058 ; -0.0018] sur 6299 courses → **meilleur que le marché**.

## Test : paris fictifs à 1 €

| Stratégie | Paris | ROI | IC 95 % | Taux de réussite |
|---|---:|---:|---|---:|
| SG modèle | 6299 | -13.1 % | [-17.3 % ; -9.4 %] | 26.8 % |
| SG favori | 6299 | -13.1 % | [-17.1 % ; -9.3 %] | 26.8 % |
| SP modèle | 6296 | -10.7 % | [-13.0 % ; -8.5 %] | 55.9 % |
| SP favori | 6296 | -11.6 % | [-13.9 % ; -9.5 %] | 55.7 % |
| SG valeur modèle | 75 | +24.7 % | [-42.4 % ; +102.1 %] | 18.7 % |
