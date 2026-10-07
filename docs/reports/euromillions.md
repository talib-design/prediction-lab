# EuroMillions — que disent 22 ans de tirages ?

Données : 1 987 tirages officiels FDJ, du 2004-02-13 au 2026-10-06. Analyse du 2026-10-06. Toutes les hypothèses ont été inscrites au registre chaîné avant le calcul (`em-A1` à `em-R2`).

**En bref.** 8 tests sur 136 sortent à p < 0,05, soit à peu près ce que le hasard seul produit (6,8). Aucun ne survit à la correction pour tests multiples. Les numéros chauds, froids, en retard ou répétés ne sortent ni plus ni moins que les autres, et aucune logique ne bat un joueur au hasard. Le seul effet net ne porte pas sur le tirage mais sur les joueurs : les petits numéros, surjoués, rapportent moins quand ils sortent.

## 1. Ce qu'on pouvait détecter

À lire avant les résultats : ce tableau borne ce que « rien de détecté » veut dire. Biais minimal sur un numéro, vu 8 fois sur 10 au seuil de 5 %.

| Groupe | Tirages | Sans correction | Corrigé (tous les numéros) |
|---|---|---|---|
| boules, 2004-2026 | 1 987 | +19 % | +28 % |
| boules, ère 2016-09 | 1 047 | +27 % | +40 % |
| étoiles 1-12, 2016-09 | 1 047 | +20 % | +26 % |
| étoiles 1-11, 2011-05 | 562 | +26 % | +34 % |
| étoiles 1-9, 2004-02 | 378 | +28 % | +36 % |

Pour les théories (section 4), la dernière colonne de leur tableau donne l'effet minimal détectable de chaque test : autour de +5 % pour les boules, +10 % pour les étoiles. Un effet plus petit peut exister sans qu'on puisse le voir avec 22 ans de tirages.

## 2. Contrôle 100 % hasard (em-R2)

Toute la batterie relancée sur 200 historiques fabriqués au hasard (136 tests chacun). Verdict : **réussi**.

| Critère inscrit | Seuil | Mesuré |
|---|---|---|
| part des p < 0,05 | entre 3 % et 7 % | 4,97 % |
| historiques avec un « signal » après BH, A1 | <= 8 % | 3,5 % |
| historiques avec un « signal » après BH, A2 | <= 8 % | 7,5 % |
| historiques avec un « signal » après BH, A3 | <= 8 % | 5,5 % |
| historiques avec un « signal » après BH, A4 | <= 8 % | 4,0 % |
| historiques avec un « signal » après BH, B | <= 8 % | 4,0 % |
| historiques avec un « signal » après BH, C1 | <= 8 % | 5,5 % |
| historiques avec un « signal » après BH, C2 | <= 8 % | 1,5 % |
| historiques avec un « signal » après BH, C3 | <= 8 % | 4,5 % |
| uniformité des p des théories (KS) | p > 0,01 | 0,779 |

## 3. Le mécanisme est-il équitable ? (A1 à A4)

| Test | Tirages | p | q (BH) |
|---|---|---|---|
| boules, tous tirages | 1987 | 0,187 | 0,328 |
| boules, époque 2004-02 | 378 | 0,788 | 0,788 |
| étoiles 1-9, époque 2004-02 | 378 | 0,632 | 0,737 |
| boules, époque 2011-05 | 562 | 0,158 | 0,328 |
| étoiles 1-11, époque 2011-05 | 562 | 0,025 | 0,176 |
| boules, époque 2016-09 | 1047 | 0,390 | 0,545 |
| étoiles 1-12, époque 2016-09 | 1047 | 0,149 | 0,328 |
| boules : mêmes fréquences dans les 3 époques | 1987 | 0,586 | 0,894 |
| boules : mardi = vendredi (2011-05) | 562 | 0,433 | 0,894 |
| étoiles : mardi = vendredi (2011-05) | 562 | 0,864 | 0,894 |
| boules : mardi = vendredi (2016-09) | 1047 | 0,894 | 0,894 |
| étoiles : mardi = vendredi (2016-09) | 1047 | 0,864 | 0,894 |

Numéro par numéro (A2) : 6 tests sur 82 à p < 0,05, pour 4,1 attendus au hasard ; 0 après correction. Les plus extrêmes :

- boule 22 (all) : 157 sorties pour 198,7 attendues (p = 0,001, q = 0,120).
- étoile 6 (2011-05) : 80 sorties pour 102,2 attendues (p = 0,014, q = 0,441).
- étoile 2 (2016-09) : 204 sorties pour 174,5 attendues (p = 0,016, q = 0,441).

Ordre d'extraction (A3) : 1 test sur 10 à p < 0,05, 0 après correction.

## 4. Les théories de prédiction (B) : chaud, froid, séries, retard

Test causal exact : à chaque tirage la règle ne regarde que le passé ; « ratio » = sorties des numéros choisis / sorties attendues au hasard (1,000 = pareil que le hasard). « 1re / 2e moitié » : avant / depuis 2020.

| Théorie | Tirages | Ratio | z | p | q | z 1re / 2e moitié | Détectable |
|---|---|---|---|---|---|---|---|
| boules chaudes : 10 plus sorties sur 20 tirages | 1687 | 0,987 | -0,69 | 0,487 | 0,935 | -0,13 / -0,91 | 1,050 |
| boules chaudes : 10 plus sorties sur 50 tirages | 1687 | 0,991 | -0,45 | 0,654 | 0,935 | -1,69 / +1,29 | 1,054 |
| boules chaudes : 10 plus sorties sur 100 tirages | 1687 | 1,001 | +0,05 | 0,961 | 0,961 | -0,51 / +0,67 | 1,055 |
| boules chaudes : 10 plus sorties sur 300 tirages | 1687 | 0,988 | -0,60 | 0,549 | 0,935 | -0,77 / -0,02 | 1,056 |
| boules froides : 10 moins sorties sur 20 tirages | 1687 | 0,980 | -1,16 | 0,247 | 0,935 | -0,88 / -0,75 | 1,048 |
| boules froides : 10 moins sorties sur 50 tirages | 1687 | 0,983 | -0,89 | 0,376 | 0,935 | +0,48 / -1,94 | 1,053 |
| boules froides : 10 moins sorties sur 100 tirages | 1687 | 0,994 | -0,29 | 0,774 | 0,937 | +1,20 / -1,87 | 1,055 |
| boules froides : 10 moins sorties sur 300 tirages | 1687 | 0,986 | -0,70 | 0,485 | 0,935 | -0,12 / -0,94 | 1,056 |
| série : boules du tirage précédent | 1687 | 0,969 | -1,00 | 0,316 | 0,935 | -1,07 / -0,29 | 1,088 |
| série : voisins ±1 des boules du tirage précédent | 1687 | 1,021 | +0,91 | 0,362 | 0,935 | +1,18 / +0,01 | 1,064 |
| retard : 10 boules au plus long retard | 1687 | 1,005 | +0,23 | 0,817 | 0,937 | -0,03 / +0,40 | 1,058 |
| retard : boules absentes depuis au moins 20 tirages | 1687 | 0,962 | -1,36 | 0,174 | 0,935 | -1,10 / -0,80 | 1,079 |
| étoiles chaudes : 3 plus sorties sur 20 tirages (2016-09) | 947 | 1,031 | +0,91 | 0,365 | 0,935 | +0,68 / +0,65 | 1,097 |
| étoiles chaudes : 3 plus sorties sur 50 tirages (2016-09) | 947 | 1,030 | +0,83 | 0,408 | 0,935 | +1,72 / -0,05 | 1,100 |
| étoiles chaudes : 3 plus sorties sur 100 tirages (2016-09) | 947 | 0,993 | -0,20 | 0,843 | 0,937 | -0,12 / -0,16 | 1,101 |
| étoiles froides : 3 moins sorties sur 20 tirages (2016-09) | 947 | 0,991 | -0,28 | 0,778 | 0,937 | -0,10 / -0,27 | 1,094 |
| étoiles froides : 3 moins sorties sur 50 tirages (2016-09) | 947 | 0,958 | -1,17 | 0,241 | 0,935 | -1,12 / -0,70 | 1,099 |
| étoiles froides : 3 moins sorties sur 100 tirages (2016-09) | 947 | 0,984 | -0,45 | 0,655 | 0,935 | +0,87 / -1,01 | 1,102 |
| série : étoiles du tirage précédent (2016-09) | 947 | 1,026 | +0,54 | 0,590 | 0,935 | +0,34 / +0,42 | 1,137 |
| retard : 3 étoiles au plus long retard (2016-09) | 947 | 1,002 | +0,06 | 0,955 | 0,961 | -1,06 / +0,69 | 1,105 |

## 5. La forme des tirages (C)

| Test | Observé | Hasard exact | p | q |
|---|---|---|---|---|
| somme des 5 boules | 127,518 | 127,500 | 0,563 | 0,845 |
| nombre de boules impaires | 2,527 | 2,500 | 0,269 | 0,732 |
| nombre de boules <= 25 | 2,512 | 2,500 | 0,662 | 0,851 |
| nombre de paires consécutives | 0,392 | 0,400 | 0,880 | 0,880 |
| dizaines distinctes | 3,443 | 3,447 | 0,871 | 0,880 |
| derniers chiffres distincts | 4,217 | 4,234 | 0,327 | 0,732 |
| étendue max-min | 34,140 | 34,000 | 0,330 | 0,732 |
| somme des 2 étoiles (2016-09) | 12,927 | 13,000 | 0,160 | 0,732 |
| étoiles consécutives (2016-09) | 164,000 | 174,500 | 0,407 | 0,732 |
| paires de tirages aux 5 mêmes boules | 1,000 | 0,931 | 0,606 | 0,606 |
| autocorrélation de la somme (rang 1) | 0,015 | -0,001 | 0,497 | 0,554 |
| Ljung-Box sur la somme (rangs 1-10) | – | – | 0,554 | 0,554 |

Combinaisons répétées : 1 paire de tirages identiques (4-30-31-38-42 les 2014-05-02 et 2018-08-31) pour 0,93 attendue au hasard ; 211 paires partagent 4 boules pour 209,5 attendues.

## 6. Logiques contre hasard, en marche avant (D1, R1)

Chaque logique joue une grille par tirage, calculée uniquement avec les tirages précédents. « Percentile » : part des 1 000 joueurs au hasard qu'elle dépasse. « Log loss » : coût de ses probabilités par rapport au tirage uniforme (négatif = mieux que le hasard).

**Boules, 2004-2026** (1 787 tirages, du 2007-12-14 au 2026-10-06). Hasard : 0,500 trouvés par tirage ; 95 % des joueurs au hasard entre 0,467 et 0,531.

| Logique | Trouvés | z | Percentile | Log loss vs uniforme [IC 95 %] | q |
|---|---|---|---|---|---|
| fréquence totale | 0,503 | +0,20 | 58 % | +0,00055 [+0,00026 ; +0,00080] | < 0,001 |
| fréquence 100 derniers | 0,509 | +0,57 | 71 % | +0,00426 [+0,00364 ; +0,00487] | < 0,001 |
| fréquence 300 derniers | 0,493 | -0,46 | 33 % | +0,00155 [+0,00115 ; +0,00194] | < 0,001 |
| fréquence rétrécie | 0,496 | -0,28 | 38 % | +0,00001 [-0,00002 ; +0,00005] | 0,460 |
| retard | 0,482 | -1,20 | 13 % | +0,04905 [+0,04647 ; +0,05182] | < 0,001 |
| chauds 50 | 0,495 | -0,31 | 38 % | +0,00140 [+0,00105 ; +0,00177] | < 0,001 |
| froids 50 | 0,491 | -0,61 | 28 % | +0,00151 [+0,00123 ; +0,00184] | < 0,001 |
| répétition | 0,486 | -0,90 | 18 % | +0,00107 [+0,00080 ; +0,00134] | < 0,001 |
| témoin hasard (R1) | 0,512 | +0.79 | – | – | – |

**Ère 2016-09, boules** (847 tirages, du 2018-08-28 au 2026-10-06). Hasard : 0,500 trouvés par tirage ; 95 % des joueurs au hasard entre 0,457 et 0,545.

| Logique | Trouvés | z | Percentile | Log loss vs uniforme [IC 95 %] | q |
|---|---|---|---|---|---|
| fréquence totale | 0,489 | -0,51 | 28 % | +0,00093 [+0,00048 ; +0,00128] | < 0,001 |
| fréquence 100 derniers | 0,518 | +0,83 | 78 % | +0,00423 [+0,00334 ; +0,00512] | < 0,001 |
| fréquence 300 derniers | 0,492 | -0,35 | 33 % | +0,00163 [+0,00111 ; +0,00215] | < 0,001 |
| fréquence rétrécie | 0,489 | -0,51 | 28 % | +0,00002 [-0,00000 ; +0,00003] | 0,032 |
| retard | 0,502 | +0,08 | 51 % | +0,04660 [+0,04293 ; +0,04986] | < 0,001 |
| chauds 50 | 0,516 | +0,72 | 75 % | +0,00120 [+0,00068 ; +0,00167] | < 0,001 |
| froids 50 | 0,455 | -2,06 | 2 % | +0,00175 [+0,00126 ; +0,00220] | < 0,001 |
| répétition | 0,472 | -1,26 | 9 % | +0,00120 [+0,00081 ; +0,00162] | < 0,001 |
| témoin hasard (R1) | 0,503 | +0.13 | – | – | – |

**Ère 2016-09, étoiles** (847 tirages, du 2018-08-28 au 2026-10-06). Hasard : 0,333 trouvés par tirage ; 95 % des joueurs au hasard entre 0,301 et 0,372.

| Logique | Trouvés | z | Percentile | Log loss vs uniforme [IC 95 %] | q |
|---|---|---|---|---|---|
| fréquence totale | 0,377 | +2,51 | 99 % | +0,00066 [-0,00022 ; +0,00171] | 0,216 |
| fréquence 100 derniers | 0,336 | +0,18 | 52 % | +0,00431 [+0,00249 ; +0,00662] | < 0,001 |
| fréquence 300 derniers | 0,358 | +1,41 | 90 % | +0,00124 [+0,00004 ; +0,00260] | 0,101 |
| fréquence rétrécie | 0,377 | +2,51 | 99 % | +0,00011 [-0,00033 ; +0,00060] | 0,666 |
| retard | 0,338 | +0,25 | 55 % | +0,07450 [+0,06502 ; +0,08406] | < 0,001 |
| chauds 50 | 0,357 | +1,34 | 88 % | +0,00241 [+0,00089 ; +0,00403] | 0,006 |
| froids 50 | 0,320 | -0,77 | 20 % | +0,00402 [+0,00258 ; +0,00535] | < 0,001 |
| répétition | 0,346 | +0,73 | 72 % | +0,00207 [+0,00054 ; +0,00359] | 0,016 |
| témoin hasard (R1) | 0,322 | -0.64 | – | – | – |

## 7. Gains fictifs, une grille par tirage (D2)

Ère 2016-09, 847 tirages, grille à 2,50 EUR (prix lu sur la page FDJ le 2026-10-06 ; constance sur toute la période non vérifiée). Payée au rapport officiel. Le jackpot n'apparaît pas : aucune grille ne l'a touché. Mesure de performance, pas une stratégie de mise.

1 000 joueurs au hasard : gain moyen médian 0,42 EUR par grille (95 % entre 0,32 et 0,58), rendement médian -83 %.

| Logique | Gain moyen / grille | IC 95 % | Rendement | Grilles gagnantes | Percentile |
|---|---|---|---|---|---|
| fréquence totale | 0,372 EUR | 0,28-0,48 | -85 % | 65 | 20 % |
| fréquence 100 derniers | 0,416 EUR | 0,32-0,52 | -83 % | 69 | 48 % |
| fréquence 300 derniers | 0,354 EUR | 0,26-0,46 | -86 % | 60 | 11 % |
| fréquence rétrécie | 0,353 EUR | 0,27-0,45 | -86 % | 64 | 10 % |
| retard | 0,373 EUR | 0,28-0,48 | -85 % | 60 | 21 % |
| chauds 50 | 0,427 EUR | 0,34-0,54 | -83 % | 73 | 55 % |
| froids 50 | 0,357 EUR | 0,27-0,45 | -86 % | 61 | 12 % |
| répétition | 0,376 EUR | 0,28-0,47 | -85 % | 63 | 23 % |
| témoin hasard (R1) | 0,388 EUR | 0,31-0,48 | -84 % | 62 | – |

Table des rangs vérifiée sur les gagnants européens : écart maximal 4,0 % entre gagnants observés et probabilités exactes.

## 8. Popularité des numéros et gains (D3, exploratoire)

Variation du rapport par gagnant pour chaque boule <= 31 en plus dans le tirage (ère 2016-09). Le tirage étant aléatoire, c'est quasiment une expérience randomisée.

| Rang | Tirages | Variation par boule <= 31 | p | Spearman |
|---|---|---|---|---|
| 3 | 1042 | -19,9 % | < 0,001 | -0,30 |
| 4 | 1047 | -13,6 % | < 0,001 | -0,25 |
| 5 | 1047 | -14,4 % | < 0,001 | -0,53 |
| 6 | 1047 | -9,4 % | < 0,001 | -0,26 |
| 7 | 1047 | -14,0 % | < 0,001 | -0,50 |
| 8 | 1047 | -6,0 % | < 0,001 | -0,22 |
| 9 | 1047 | -10,4 % | < 0,001 | -0,53 |
| 10 | 1047 | -10,5 % | < 0,001 | -0,55 |
| 11 | 1047 | -1,4 % | 0,116 | -0,04 |
| 12 | 1047 | -6,0 % | < 0,001 | -0,32 |
| 13 | 1047 | -6,6 % | < 0,001 | -0,66 |

Lecture : les joueurs surjouent les petits numéros (dates de naissance). Quand ils sortent, les gagnants sont plus nombreux et chacun touche moins. Cela ne change pas la probabilité de gagner, seulement le montant quand on gagne.

## 9. Carnet à terme : les tirages à venir (F1, R1)

Aucun tirage noté pour l'instant.

Grilles figées en attente du tirage :

| Tirage | Logique | Grille |
|---|---|---|
| 2026-10-09 | fréquence totale | 10 17 29 42 44 ★ 02 03 |
| 2026-10-09 | fréquence 100 derniers | 08 10 14 17 44 ★ 02 10 |
| 2026-10-09 | fréquence 300 derniers | 08 10 13 29 42 ★ 09 12 |
| 2026-10-09 | fréquence rétrécie | 10 17 29 42 44 ★ 02 03 |
| 2026-10-09 | retard | 06 20 21 36 43 ★ 05 09 |
| 2026-10-09 | chauds 50 | 02 08 10 45 47 ★ 02 08 |
| 2026-10-09 | froids 50 | 01 20 21 24 27 ★ 03 07 |
| 2026-10-09 | répétition | 18 22 32 41 48 ★ 08 10 |
| 2026-10-09 | témoin hasard (R1) | 14 30 36 40 44 ★ 08 11 |

Ce qu'il faudra pour conclure : une logique qui trouverait +0,1 boule par tirage demande environ 325 tirages (3 ans) pour être vue ; +0,15 environ 145 tirages.

## 10. Conclusion

Sur l'historique, le tirage EuroMillions se comporte comme un hasard équitable et sans mémoire, à la précision que 1 987 tirages permettent : un biais de 19 % sur une boule désignée d'avance (28 % sur n'importe laquelle des 50), ou un effet chaud / froid / retard de 5 à 10 %, aurait été vu 8 fois sur 10. Rien de tel. Le juge définitif reste le carnet à terme, qui fait jouer chaque logique et le témoin hasard sur tous les tirages à venir.

*Rapport régénéré par `predlab lottery report` à partir de `data/lottery/*.json`.*
