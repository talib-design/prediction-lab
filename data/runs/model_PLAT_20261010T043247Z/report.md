# Modèle Marché+ — plat

Généré le 2026-10-10T04:32:47+00:00 · courses : apprentissage 13610, réglage 3644, test 6383 · λ = 1 · α du marché seul = 1.090.

## Ce que chaque facteur ajoute à la cote (fenêtre d'apprentissage)

Effet = chances de gagner multipliées par ce nombre pour un écart-type de plus du facteur, *à cote égale*. ×1,00 : la cote l'avait déjà intégré.

| Facteur | β | IC 95 % | Effet par écart-type | p |
|---|---:|---|---:|---:|
| Cote (marché) | 1.065 | [1.038 ; 1.093] | — | 0.000 |
| Forme : places gagnées sur la cote, courses passées | 0.012 | [-0.012 ; 0.036] | ×1.012 | 0.328 |
| Préférence du cheval pour ce terrain | 0.061 | [0.039 ; 0.082] | ×1.062 | 0.000 |
| Préférence du cheval pour cette température | 0.032 | [0.009 ; 0.055] | ×1.033 | 0.006 |
| Aucune course connue depuis 2024 | -0.013 | [-0.056 ; 0.030] | ×0.987 | 0.549 |
| Repos (log des jours depuis la dernière course) | -0.032 | [-0.072 ; 0.007] | ×0.968 | 0.110 |
| Jockey / driver : victoires vs cote | 0.043 | [0.023 ; 0.063] | ×1.044 | 0.000 |
| Entraîneur : victoires vs cote | 0.058 | [0.038 ; 0.079] | ×1.060 | 0.000 |
| Position au départ (0 = intérieur, 1 = extérieur) | -0.012 | [-0.031 ; 0.007] | ×0.988 | 0.207 |
| Position au départ, sprints du plat | 0.018 | [-0.001 ; 0.036] | ×1.018 | 0.057 |
| Poids porté vs moyenne de la course (kg) | 0.055 | [0.035 ; 0.074] | ×1.056 | 0.000 |
| Recul au trot (par 25 m) | — | inactif (aucune variation) | — | — |

## Réglage : log loss par course (plus bas = mieux)

Modèle 2.0794 · marché calibré 2.0888 · différence -0.0094 [-0.0128 ; -0.0057] sur 3644 courses → **meilleur que le marché**.

## Test (décision) : log loss par course (plus bas = mieux)

Modèle 2.0895 · marché calibré 2.0951 · différence -0.0056 [-0.0085 ; -0.0030] sur 6383 courses → **meilleur que le marché**.

## Test : paris fictifs à 1 €

| Stratégie | Paris | ROI | IC 95 % | Taux de réussite |
|---|---:|---:|---|---:|
| SG modèle | 6383 | -12.8 % | [-17.0 % ; -8.8 %] | 26.8 % |
| SG favori | 6383 | -12.8 % | [-16.8 % ; -8.8 %] | 26.9 % |
| SP modèle | 6380 | -10.3 % | [-12.4 % ; -8.2 %] | 56.3 % |
| SP favori | 6380 | -11.4 % | [-13.6 % ; -9.4 %] | 55.9 % |
| SG valeur modèle | 843 | -15.6 % | [-33.9 % ; +4.2 %] | 12.5 % |
