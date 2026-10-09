# Modèle Marché+ — trot attelé

Généré le 2026-10-09T04:48:14+00:00 · courses : apprentissage 10271, réglage 4076, test 7237 · λ = 1 · α du marché seul = 1.138.

## Ce que chaque facteur ajoute à la cote (fenêtre d'apprentissage)

Effet = chances de gagner multipliées par ce nombre pour un écart-type de plus du facteur, *à cote égale*. ×1,00 : la cote l'avait déjà intégré.

| Facteur | β | IC 95 % | Effet par écart-type | p |
|---|---:|---|---:|---:|
| Cote (marché) | 1.115 | [1.090 ; 1.140] | — | 0.000 |
| Forme : places gagnées sur la cote, courses passées | -0.034 | [-0.061 ; -0.007] | ×0.967 | 0.014 |
| Préférence du cheval pour ce terrain | 0.005 | [-0.017 ; 0.026] | ×1.005 | 0.672 |
| Préférence du cheval pour cette température | 0.008 | [-0.018 ; 0.035] | ×1.008 | 0.531 |
| Aucune course connue depuis 2024 | 0.006 | [-0.037 ; 0.048] | ×1.006 | 0.800 |
| Repos (log des jours depuis la dernière course) | -0.016 | [-0.057 ; 0.025] | ×0.984 | 0.433 |
| Jockey / driver : victoires vs cote | 0.032 | [0.007 ; 0.056] | ×1.032 | 0.012 |
| Entraîneur : victoires vs cote | 0.052 | [0.027 ; 0.077] | ×1.053 | 0.000 |
| Position au départ (0 = intérieur, 1 = extérieur) | -0.039 | [-0.061 ; -0.017] | ×0.962 | 0.001 |
| Position au départ, sprints du plat | — | inactif (aucune variation) | — | — |
| Poids porté vs moyenne de la course (kg) | — | inactif (aucune variation) | — | — |
| Recul au trot (par 25 m) | -0.037 | [-0.065 ; -0.010] | ×0.963 | 0.008 |

## Réglage : log loss par course (plus bas = mieux)

Modèle 2.0271 · marché calibré 2.0310 · différence -0.0038 [-0.0060 ; -0.0016] sur 4076 courses → **meilleur que le marché**.

## Test (décision) : log loss par course (plus bas = mieux)

Modèle 1.9720 · marché calibré 1.9758 · différence -0.0038 [-0.0054 ; -0.0021] sur 7237 courses → **meilleur que le marché**.

## Test : paris fictifs à 1 €

| Stratégie | Paris | ROI | IC 95 % | Taux de réussite |
|---|---:|---:|---|---:|
| SG modèle | 7237 | -12.0 % | [-15.1 % ; -8.6 %] | 32.7 % |
| SG favori | 7237 | -11.4 % | [-14.4 % ; -8.3 %] | 32.9 % |
| SP modèle | 7237 | -7.8 % | [-9.7 % ; -5.8 %] | 58.5 % |
| SP favori | 7237 | -6.9 % | [-8.7 % ; -5.0 %] | 59.0 % |
| SG valeur modèle | 27 | -31.5 % | [-70.4 % ; +18.9 %] | 22.2 % |
