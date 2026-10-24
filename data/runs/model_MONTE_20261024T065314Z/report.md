# Modèle Marché+ — trot monté

Généré le 2026-10-24T06:53:14+00:00 · courses : apprentissage 1076, réglage 802, test 1384 · λ = 1000 · α du marché seul = 1.087.

## Ce que chaque facteur ajoute à la cote (fenêtre d'apprentissage)

Effet = chances de gagner multipliées par ce nombre pour un écart-type de plus du facteur, *à cote égale*. ×1,00 : la cote l'avait déjà intégré.

| Facteur | β | IC 95 % | Effet par écart-type | p |
|---|---:|---|---:|---:|
| Cote (marché) | 1.084 | [1.008 ; 1.160] | — | 0.000 |
| Forme : places gagnées sur la cote, courses passées | 0.009 | [-0.038 ; 0.056] | ×1.009 | 0.708 |
| Préférence du cheval pour ce terrain | -0.009 | [-0.050 ; 0.032] | ×0.991 | 0.664 |
| Préférence du cheval pour cette température | -0.014 | [-0.061 ; 0.033] | ×0.986 | 0.564 |
| Aucune course connue depuis 2024 | -0.001 | [-0.054 ; 0.051] | ×0.999 | 0.955 |
| Repos (log des jours depuis la dernière course) | 0.019 | [-0.033 ; 0.071] | ×1.019 | 0.467 |
| Jockey / driver : victoires vs cote | 0.010 | [-0.036 ; 0.056] | ×1.010 | 0.675 |
| Entraîneur : victoires vs cote | -0.011 | [-0.056 ; 0.034] | ×0.989 | 0.636 |
| Position au départ (0 = intérieur, 1 = extérieur) | 0.032 | [-0.013 ; 0.077] | ×1.032 | 0.167 |
| Position au départ, sprints du plat | — | inactif (aucune variation) | — | — |
| Poids porté vs moyenne de la course (kg) | 0.020 | [-0.028 ; 0.068] | ×1.020 | 0.420 |
| Recul au trot (par 25 m) | -0.027 | [-0.078 ; 0.023] | ×0.973 | 0.288 |

## Réglage : log loss par course (plus bas = mieux)

Modèle 1.9182 · marché calibré 1.9195 · différence -0.0013 [-0.0036 ; 0.0009] sur 802 courses → **pas de différence démontrée**.

## Test (décision) : log loss par course (plus bas = mieux)

Modèle 1.9508 · marché calibré 1.9521 · différence -0.0012 [-0.0032 ; 0.0005] sur 1384 courses → **pas de différence démontrée**.

## Test : paris fictifs à 1 €

| Stratégie | Paris | ROI | IC 95 % | Taux de réussite |
|---|---:|---:|---|---:|
| SG modèle | 1384 | -12.7 % | [-19.8 % ; -5.4 %] | 33.5 % |
| SG favori | 1384 | -12.6 % | [-20.0 % ; -5.3 %] | 33.5 % |
| SP modèle | 1384 | -8.3 % | [-12.2 % ; -3.8 %] | 59.4 % |
| SP favori | 1384 | -9.0 % | [-12.8 % ; -4.7 %] | 59.0 % |
| SG valeur modèle | 3 | — | — | — |
