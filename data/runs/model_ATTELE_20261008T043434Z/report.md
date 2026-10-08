# Modèle Marché+ — trot attelé

Généré le 2026-10-08T04:34:34+00:00 · courses : apprentissage 4685, réglage 4076, test 7224 · λ = 100 · α du marché seul = 1.129.

## Ce que chaque facteur ajoute à la cote (fenêtre d'apprentissage)

Effet = chances de gagner multipliées par ce nombre pour un écart-type de plus du facteur, *à cote égale*. ×1,00 : la cote l'avait déjà intégré.

| Facteur | β | IC 95 % | Effet par écart-type | p |
|---|---:|---|---:|---:|
| Cote (marché) | 1.111 | [1.074 ; 1.147] | — | 0.000 |
| Forme : places gagnées sur la cote, courses passées | -0.032 | [-0.070 ; 0.006] | ×0.968 | 0.095 |
| Préférence du cheval pour ce terrain | 0.010 | [-0.024 ; 0.043] | ×1.010 | 0.569 |
| Préférence du cheval pour cette température | 0.009 | [-0.028 ; 0.046] | ×1.009 | 0.633 |
| Aucune course connue depuis 2024 | 0.019 | [-0.049 ; 0.087] | ×1.019 | 0.582 |
| Repos (log des jours depuis la dernière course) | 0.036 | [-0.030 ; 0.101] | ×1.036 | 0.284 |
| Jockey / driver : victoires vs cote | 0.060 | [0.026 ; 0.094] | ×1.062 | 0.001 |
| Entraîneur : victoires vs cote | 0.028 | [-0.006 ; 0.063] | ×1.029 | 0.109 |
| Position au départ (0 = intérieur, 1 = extérieur) | -0.034 | [-0.067 ; -0.002] | ×0.966 | 0.037 |
| Position au départ, sprints du plat | — | inactif (aucune variation) | — | — |
| Poids porté vs moyenne de la course (kg) | — | inactif (aucune variation) | — | — |
| Recul au trot (par 25 m) | -0.037 | [-0.078 ; 0.003] | ×0.963 | 0.070 |

## Réglage : log loss par course (plus bas = mieux)

Modèle 2.0276 · marché calibré 2.0308 · différence -0.0032 [-0.0054 ; -0.0006] sur 4076 courses → **meilleur que le marché**.

## Test (décision) : log loss par course (plus bas = mieux)

Modèle 1.9711 · marché calibré 1.9754 · différence -0.0043 [-0.0061 ; -0.0025] sur 7224 courses → **meilleur que le marché**.

## Test : paris fictifs à 1 €

| Stratégie | Paris | ROI | IC 95 % | Taux de réussite |
|---|---:|---:|---|---:|
| SG modèle | 7224 | -12.0 % | [-15.1 % ; -8.6 %] | 32.7 % |
| SG favori | 7224 | -11.4 % | [-14.3 % ; -8.2 %] | 32.9 % |
| SP modèle | 7224 | -7.4 % | [-9.2 % ; -5.3 %] | 58.7 % |
| SP favori | 7224 | -6.9 % | [-8.6 % ; -4.9 %] | 59.0 % |
| SG valeur modèle | 48 | -2.3 % | [-36.7 % ; +44.4 %] | 31.2 % |
