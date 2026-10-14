# Modèle Marché+ — plat

Généré le 2026-10-14T23:33:44+00:00 · courses : apprentissage 13610, réglage 3644, test 6443 · λ = 10 · α du marché seul = 1.090.

## Ce que chaque facteur ajoute à la cote (fenêtre d'apprentissage)

Effet = chances de gagner multipliées par ce nombre pour un écart-type de plus du facteur, *à cote égale*. ×1,00 : la cote l'avait déjà intégré.

| Facteur | β | IC 95 % | Effet par écart-type | p |
|---|---:|---|---:|---:|
| Cote (marché) | 0.360 | [0.236 ; 0.484] | — | 0.000 |
| Forme : places gagnées sur la cote, courses passées | 0.014 | [-0.010 ; 0.038] | ×1.014 | 0.261 |
| Préférence du cheval pour ce terrain | 0.059 | [0.038 ; 0.081] | ×1.061 | 0.000 |
| Préférence du cheval pour cette température | 0.032 | [0.009 ; 0.054] | ×1.032 | 0.007 |
| Aucune course connue depuis 2024 | 0.002 | [-0.041 ; 0.045] | ×1.002 | 0.918 |
| Repos (log des jours depuis la dernière course) | -0.016 | [-0.056 ; 0.023] | ×0.984 | 0.412 |
| Jockey / driver : victoires vs cote | 0.042 | [0.023 ; 0.062] | ×1.043 | 0.000 |
| Entraîneur : victoires vs cote | 0.056 | [0.035 ; 0.077] | ×1.058 | 0.000 |
| Position au départ (0 = intérieur, 1 = extérieur) | -0.009 | [-0.028 ; 0.009] | ×0.991 | 0.332 |
| Position au départ, sprints du plat | 0.018 | [-0.000 ; 0.036] | ×1.018 | 0.053 |
| Poids porté vs moyenne de la course (kg) | 0.049 | [0.030 ; 0.068] | ×1.050 | 0.000 |
| Recul au trot (par 25 m) | — | inactif (aucune variation) | — | — |
| c_logq2 | -0.642 | [-0.753 ; -0.531] | ×0.526 | 0.000 |

## Réglage : log loss par course (plus bas = mieux)

Modèle 2.0747 · marché calibré 2.0888 · différence -0.0141 [-0.0188 ; -0.0095] sur 3644 courses → **meilleur que le marché**.

## Test (décision) : log loss par course (plus bas = mieux)

Modèle 2.0824 · marché calibré 2.0940 · différence -0.0116 [-0.0150 ; -0.0079] sur 6443 courses → **meilleur que le marché**.

## Test : paris fictifs à 1 €

| Stratégie | Paris | ROI | IC 95 % | Taux de réussite |
|---|---:|---:|---|---:|
| SG modèle | 6443 | -13.0 % | [-17.2 % ; -9.1 %] | 26.8 % |
| SG favori | 6443 | -13.1 % | [-16.8 % ; -9.2 %] | 26.9 % |
| SP modèle | 6440 | -10.4 % | [-12.6 % ; -8.4 %] | 56.2 % |
| SP favori | 6440 | -11.5 % | [-13.5 % ; -9.4 %] | 55.8 % |
| SG valeur modèle | 1502 | -9.1 % | [-20.7 % ; +2.1 %] | 15.1 % |
