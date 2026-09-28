# Journal — Loto, 1 mois

Un cycle par tirage : **résultat → score → analyse → apprentissage → nouvelle
prédiction**. Le bilan chiffré cumulé est dans `BILAN.md`, les données brutes et
chaînées dans `journal.jsonl`, les règles dans `PROTOCOLE.md`.

---

## Cycle 0 — samedi 26/09/2026 (mise en place, 16h45)

**Rattrapage des données.** L'archive FDJ locale s'arrêtait au 16/09. J'ai ajouté les
tirages du 19, du 21 et du 23/09, chacun vérifié sur fdj.fr et sur une seconde source.

**Apprentissage initial.** Sur les 30 derniers tirages, le réglage retenu est
*demi-vie 10, mode froid* : jouer les numéros les **moins** sortis récemment. Il a
trouvé 18 bons numéros là où le hasard en donne 15,3 en moyenne. Cet écart est
inférieur à un écart-type (≈ 3,5 sur 30 tirages). Choisir le meilleur de 12
réglages sur 30 tirages revient presque à désigner le plus chanceux. C'est
justement ce que l'expérience doit mettre à l'épreuve.

**Prédiction pour le samedi 26/09/2026**

| Grille | Numéros | Chance |
|---|---|---|
| adaptatif (h=10, froid) | 19 · 25 · 33 · 42 · 47 | 8 |
| frequence | 5 · 15 · 24 · 30 · 31 | 2 |
| hasard | 2 · 8 · 12 · 40 · 47 | 3 |

À noter : la grille `frequence` est identique à celle du 21/09. Sur plus de 1 000
tirages, trois de plus ne changent pas le classement. Elle restera probablement la
même tout le mois.

---

## Note — samedi 26/09/2026, 18h (hors cycle)

Un cycle planifié a tourné à 17h52, avant la publication du tirage. Il n'a rien enregistré.
Pour que ça ne se reproduise pas, `cycle.py` a reçu trois garde-fous et une commande `next`
(voir l'amendement dans `PROTOCOLE.md`). J'ai aussi ajouté un passage de rattrapage le
lendemain matin de chaque tirage. Le journal chaîné reste intègre, et la prédiction du
26/09 (Cycle 0) est inchangée.

---

## Cycle 1 — samedi 26/09/2026

**Résultat.** 4 · 7 · 14 · 18 · 20, chance 1. Lu sur fdj.fr et lesbonsnumeros.com (rapports-tirage-loto-2892), identique sur les deux. loto-stats.fr ne l'avait pas encore publié (404).

**Score.**

| Grille | Bons numéros | Chance | Rang | Gain simulé |
|---|---|---|---|---|
| adaptatif | 0/5 | non | — | 0 € (perdu) |
| frequence | 0/5 | non | — | 0 € (perdu) |
| hasard | 0/5 | non | — | 0 € (perdu) |

Cumul : 0 bon numéro par grille, contre 0,51 attendu au hasard. p = 1,00 pour les trois.

**Argent.** Mise cumulée : 2,20 € par grille. Gains : 0 € pour les trois, car aucune n'atteint un rang. Net : −2,20 € par grille, taux de retour 0 %. Les rapports du 26/09 ne sont pas encore enregistrés : lesbonsnumeros.com publie le tableau complet, mais fdj.fr n'affiche que les rangs 1 et 2, et loto-stats.fr ne l'a pas encore. Il manque donc une seconde source. L'espérance d'une grille au hasard pour ce tirage sera calculée quand ils seront ajoutés.

**Analyse.** Trois grilles à 0 sur 5. Au hasard, une grille fait 0 bon numéro avec une probabilité de 57 % (C(44,5)/C(49,5)). Les trois à 0 ensemble : ≈ 18 %. Rien d'anormal. Un tirage ne dit rien. Avec 1 tirage sur 14, aucune p-valeur n'est interprétable. Le seuil de décision (p < 0,0167) exige environ 14 bons numéros sur le mois pour une grille, contre 7,1 attendus. On en est à 0.

**Apprentissage.** `learn` garde demi-vie 10, mode froid : 18 bons numéros sur les 30 derniers tirages, contre 15,3 attendus au hasard (lift 0,97). Les réglages suivants sont tous à 15. L'avance du réglage retenu (+2,7) reste sous un écart-type (≈ 3,5). Rien n'a bougé, et c'est normal : un tirage de plus dans une fenêtre de 30 ne déplace presque rien. Le 4-7-14-18-20 ne touchait aucun des numéros « froids » joués. Ils restent donc les moins sortis, et la grille adaptative du 28/09 est **identique** à celle du 26/09. Ce n'est pas un signal, c'est la mécanique du mode froid.

**Nouvelle prédiction — lundi 28/09/2026**

| Grille | Numéros | Chance |
|---|---|---|
| adaptatif (h=10, froid) | 19 · 25 · 33 · 42 · 47 | 8 |
| frequence | 5 · 15 · 24 · 30 · 31 | 2 |
| hasard | 2 · 5 · 23 · 45 · 49 | 3 |

---

## Arrêt — lundi 28/09/2026 (décision de Chris)

Expérience abandonnée après 1 tirage noté sur 14 (26/09 : 0/5 pour les trois grilles).
Les deux tâches planifiées sont désactivées. La prédiction du 28/09, déjà enregistrée, ne sera pas notée.
Aucune conclusion statistique n'est possible sur un seul tirage. Fichiers et journal chaîné conservés en l'état.
