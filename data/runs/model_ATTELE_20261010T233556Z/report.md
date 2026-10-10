# Modèle Marché+ — trot attelé

Généré le 2026-10-10T23:35:56+00:00 · courses : apprentissage 15555, réglage 4076, test 7263 · λ = 1 · α du marché seul = 1.149.

## Ce que chaque facteur ajoute à la cote (fenêtre d'apprentissage)

Effet = chances de gagner multipliées par ce nombre pour un écart-type de plus du facteur, *à cote égale*. ×1,00 : la cote l'avait déjà intégré.

| Facteur | β | IC 95 % | Effet par écart-type | p |
|---|---:|---|---:|---:|
| Cote (marché) | 1.125 | [1.104 ; 1.145] | — | 0.000 |
| Forme : places gagnées sur la cote, courses passées | -0.037 | [-0.060 ; -0.015] | ×0.963 | 0.001 |
| Préférence du cheval pour ce terrain | 0.009 | [-0.009 ; 0.027] | ×1.009 | 0.308 |
| Préférence du cheval pour cette température | 0.023 | [0.002 ; 0.045] | ×1.024 | 0.035 |
| Aucune course connue depuis 2024 | -0.009 | [-0.042 ; 0.024] | ×0.991 | 0.599 |
| Repos (log des jours depuis la dernière course) | -0.015 | [-0.046 ; 0.017] | ×0.986 | 0.366 |
| Jockey / driver : victoires vs cote | 0.039 | [0.018 ; 0.060] | ×1.040 | 0.000 |
| Entraîneur : victoires vs cote | 0.062 | [0.041 ; 0.083] | ×1.064 | 0.000 |
| Position au départ (0 = intérieur, 1 = extérieur) | -0.034 | [-0.052 ; -0.016] | ×0.967 | 0.000 |
| Position au départ, sprints du plat | — | inactif (aucune variation) | — | — |
| Poids porté vs moyenne de la course (kg) | — | inactif (aucune variation) | — | — |
| Recul au trot (par 25 m) | -0.056 | [-0.078 ; -0.033] | ×0.946 | 0.000 |

## Réglage : log loss par course (plus bas = mieux)

Modèle 2.0265 · marché calibré 2.0312 · différence -0.0047 [-0.0073 ; -0.0021] sur 4076 courses → **meilleur que le marché**.

## Test (décision) : log loss par course (plus bas = mieux)

Modèle 1.9722 · marché calibré 1.9765 · différence -0.0043 [-0.0060 ; -0.0023] sur 7263 courses → **meilleur que le marché**.

## Test : paris fictifs à 1 €

| Stratégie | Paris | ROI | IC 95 % | Taux de réussite |
|---|---:|---:|---|---:|
| SG modèle | 7263 | -10.9 % | [-14.0 % ; -7.7 %] | 33.0 % |
| SG favori | 7263 | -11.4 % | [-14.3 % ; -8.5 %] | 32.9 % |
| SP modèle | 7262 | -7.5 % | [-9.3 % ; -5.5 %] | 58.7 % |
| SP favori | 7262 | -6.9 % | [-8.7 % ; -5.0 %] | 59.0 % |
| SG valeur modèle | 77 | -9.9 % | [-44.8 % ; +29.2 %] | 27.3 % |
