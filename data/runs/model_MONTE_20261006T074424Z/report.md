# Modèle Marché+ — trot monté

Généré le 2026-10-06T07:44:24+00:00 · courses : apprentissage 379, réglage 423, test 1340 · λ = 100 · α du marché seul = 1.047.

## Ce que chaque facteur ajoute à la cote (fenêtre d'apprentissage)

Effet = chances de gagner multipliées par ce nombre pour un écart-type de plus du facteur, *à cote égale*. ×1,00 : la cote l'avait déjà intégré.

| Facteur | β | IC 95 % | Effet par écart-type | p |
|---|---:|---|---:|---:|
| Cote (marché) | 1.048 | [0.916 ; 1.181] | — | 0.000 |
| Forme : places gagnées sur la cote, courses passées | -0.023 | [-0.132 ; 0.087] | ×0.978 | 0.686 |
| Préférence du cheval pour ce terrain | — | inactif (aucune variation) | — | — |
| Préférence du cheval pour cette température | 0.063 | [-0.046 ; 0.172] | ×1.065 | 0.259 |
| Aucune course connue depuis 2024 | -0.028 | [-0.172 ; 0.115] | ×0.972 | 0.699 |
| Repos (log des jours depuis la dernière course) | 0.014 | [-0.129 ; 0.157] | ×1.014 | 0.848 |
| Jockey / driver : victoires vs cote | -0.029 | [-0.126 ; 0.067] | ×0.971 | 0.552 |
| Entraîneur : victoires vs cote | -0.020 | [-0.117 ; 0.077] | ×0.980 | 0.691 |
| Position au départ (0 = intérieur, 1 = extérieur) | — | inactif (aucune variation) | — | — |
| Position au départ, sprints du plat | — | inactif (aucune variation) | — | — |
| Poids porté vs moyenne de la course (kg) | 0.063 | [-0.046 ; 0.172] | ×1.065 | 0.256 |
| Recul au trot (par 25 m) | -0.068 | [-0.188 ; 0.053] | ×0.935 | 0.270 |

## Réglage : log loss par course (plus bas = mieux)

Modèle 1.8608 · marché calibré 1.8635 · différence -0.0027 [-0.0114 ; 0.0058] sur 423 courses → **pas de différence démontrée**.

## Test (décision) : log loss par course (plus bas = mieux)

Modèle 1.9604 · marché calibré 1.9534 · différence 0.0070 [0.0015 ; 0.0123] sur 1340 courses → **pire que le marché**.

## Test : paris fictifs à 1 €

| Stratégie | Paris | ROI | IC 95 % | Taux de réussite |
|---|---:|---:|---|---:|
| SG modèle | 1340 | -12.5 % | [-18.9 % ; -4.6 %] | 33.5 % |
| SG favori | 1340 | -13.4 % | [-19.9 % ; -5.9 %] | 33.4 % |
| SP modèle | 1340 | -9.1 % | [-13.6 % ; -4.6 %] | 59.2 % |
| SP favori | 1340 | -9.2 % | [-13.3 % ; -5.0 %] | 59.0 % |
| SG valeur modèle | 65 | -24.3 % | [-100.0 % ; +118.4 %] | 3.1 % |
