# Journal de l'agent critique — football

Une entrée par semaine, la plus récente en tête (METHODOLOGY §14). Tous les chiffres
viennent du dossier de la semaine (`data/runs/football_dossier_<jour>/dossier.json`, produit
par `predlab football dossier`) ; ce qui vient d'ailleurs (journaux) est signalé comme tel
et donné sans chiffre. L'agent critique ne touche ni au modèle, ni au carnet, ni au registre
des hypothèses, ni aux seuils. Aucun conseil de pari, aucune mise.

Lecture du dossier, à ne pas oublier :

- Les matchs terminés avant le premier passage de l'agent ne comptent pas comme manqués.
- Un banc de signaux « REJETÉ » dit que le gain est inférieur au seuil pré-enregistré, pas que
  le signal n'existe pas : la borne haute de l'intervalle à 95 % dit ce qui reste possible.
- Le « plancher de détection » du rapport est calculé sur le gain ajusté ; il rétrécit quand le
  signal n'apporte rien. Se fier à l'intervalle, pas au plancher.
- Le verdict fb-H8 (dérivation plus/moins 2,5 buts) n'est lisible qu'à partir de 100 matchs
  notés ; avant, un écart de log loss n'a pas de sens.
- La structure du marché (désaccord entre bookmakers, Pinnacle contre moyenne) est
  descriptive sur un seul relevé : ce n'est ni un signal, ni un verdict.

<!-- Les entrées commencent ici : « ## Semaine du AAAA-MM-JJ au AAAA-MM-JJ » -->

## Semaine du 2026-10-19 au 2026-10-25

Première entrée du journal. Source des chiffres : `data/runs/football_dossier_2026-10-25/` (généré le 2026-10-25 à 19 h 08 UTC). Ce qui vient des journaux (`data/logs/`) est signalé comme tel, sans chiffre.

### a. Agent automatique

- État maintenant : dernier passage il y a 2 min (attendu toutes les 5 min), pas d'alerte, journal d'erreurs vide (0 ligne).
- Passages : 882 sur 1 404 attendus depuis le premier passage (2026-10-20 à 22 h 11 UTC), soit 62,8 %. Avant cette date l'agent n'existait pas.
- 22 trous de plus de 30 minutes, aucun avec un match à couvrir (le dernier match terminé date du 21/10). Le plus long dure 478 min (du 24/10 à 20 h 50 au 25/10 à 04 h 48 UTC). Les autres vont de 39 à 241 min.
  21 des 22 trous commencent à partir du 23/10 à 23 h 33 UTC ; du 20 au 23/10 il n'y en a eu qu'un seul (96 min, le 22/10 au matin). La régularité s'est donc dégradée depuis le 24/10.
- 6 trous durent plus de 119 min (241, 196, 478, 183, 138 et 166 min). Or le gel d'une prévision se fait dans une fenêtre qui va de 2 h à 1 min avant le coup d'envoi (`docs/FOOTBALL.md`, code `forward.py`) : un trou de cette taille tombant avant un coup d'envoi ferait manquer le gel. Aucun cas pour l'instant ; la prochaine épreuve réelle est le 03/11 (20 h 00 UTC).
- Cause des trous : Je ne sais pas. Le journal de maintien en éveil (`keepawake.log`) contient « relâché : batterie sous 10 % » à des heures qui coïncident avec le début de deux trous (22/10 matin, 25/10 après-midi). Rien dans ce journal n'explique les trous du 24/10 et du début du 25/10.

### b. Captures et crédits de cotes

- Calendrier : 112 relevés réussis, 0 échec, dernier le 2026-10-25 à 07 h 51 UTC.
- Cotes : 17 réussis, 0 échec, dernier le 2026-10-21 à 21 h 03 UTC. Le journal de l'agent dit « prochain match à plus de 30 h » : pas de capture de cotes tant qu'aucun match n'est proche. Je ne sais pas si ce délai est voulu pour le 03/11, le dossier ne le dit pas.
- Scores : 25 réussis, 0 échec, dernier le 2026-10-21 à 21 h 03 UTC. Le compteur dit que l'appel passe, pas que The Odds API renvoie des matchs de football : Je ne sais pas.
- Crédits de cotes ce mois-ci : 59 sur un plafond de 400.

### c. Matchs de la semaine

- 18 matchs terminés sur 7 jours. 9 (ceux du 20/10, coup d'envoi à 16 h 45 ou 19 h 00 UTC) ont fini avant le premier passage de l'agent à 22 h 11 : impossibles à figer, ce n'est pas un défaut.
- Les 9 matchs du 21/10 sont tous figés à temps, réglés et notés. Manqués alors que l'agent tournait : 0 (la seule colonne qui compte).
- Aucun match non noté pour cause de prolongation ou de tirs au but : la phase de ligue n'en comporte pas. Les 9 matchs non notés sont uniquement ceux d'avant l'agent. Le cas prolongation / tirs au but (valeurs de `score.duration`) n'a donc pas encore été vu sur une vraie capture.

### d. Carnet et puissance

- 9 matchs notés sur les 100 requis pour fb-H8. Aucun écart n'est lisible : à 9 matchs, la demi-largeur de l'intervalle à 95 % est de 0,0402 (log loss, écart plus/moins 2,5 buts dérivé contre marché) ; à 100 matchs elle serait de 0,0121.
- Pour mémoire, le contrôle sur 5 553 matchs historiques (`football_derive_2026-10-17`) donne un écart moyen de +0,0028 et un écart-type par match de 0,062. Si cet écart se confirme, il faudrait 1 897 matchs notés pour que l'intervalle exclue zéro. À quelques matchs de ligue de coupe par semaine, c'est hors de portée à court terme.
- Chiffres des 9 matchs, à titre de relevé et sans lecture possible : 1X2, log loss du marché 0,8464 et du labo 0,8450 ; plus de 2,5 buts prévu 68,2 % pour 77,8 % observé (log loss 0,5920) ; les deux marquent prévu 62,2 % pour 66,7 % observé (log loss 0,6494) ; score exact, favori du modèle trouvé 0 fois sur 9.

### e. Hypothèses

- Registre : fb-H1 à fb-H8 PROPOSED (révision 0), fb-H9 à fb-H14 REJECTED (révision 1). fb-H8 attend les 100 matchs notés.
- Banc de signaux `football_signals_2026-10-21` (protocole football-signals-v1), gain moyen en log loss par match contre la cote recalibrée, intervalle à 95 % :
  fb-H9 repos et calendrier : -0,00002 [-0,00008 ; +0,00003], 13 430 matchs de test.
  fb-H10 forme en tirs cadrés : -0,00001 [-0,00009 ; +0,00007], 13 310 matchs.
  fb-H11 mouvement de Pinnacle : +0,00000 [-0,00003 ; +0,00003], 13 421 matchs.
  fb-H12 meilleure cote contre moyenne : -0,00005 [-0,00026 ; +0,00016], 7 379 matchs.
  fb-H13 Pinnacle contre moyenne : -0,00012 [-0,00054 ; +0,00028], 6 228 matchs.
  fb-H14 calibration du marché (contrôle) : +0,00031 [-0,00005 ; +0,00066], 13 430 matchs.
- Lecture : « rejeté » veut dire sous le seuil de 0,001 pré-enregistré, pas « le signal n'existe pas ». Les bornes hautes laissent possible un gain de +0,00003 (fb-H9, fb-H11), +0,00007 (fb-H10), +0,00016 (fb-H12), +0,00028 (fb-H13) et +0,00066 (fb-H14) de log loss par match, toutes sous 0,001. Les deux intervalles les plus larges sont ceux de fb-H13 et fb-H14 ; fb-H13 s'appuie sur le plus petit échantillon de test (6 228 matchs).
- Ces tests portent sur des championnats. Leur transfert à la Ligue des champions n'est pas testé : Je ne sais pas. Aucun nouveau rapport depuis celui du 2026-10-21 ; rien n'a changé sur les hypothèses cette semaine.

### f. Structure du marché

- Le dernier relevé de cotes date du 2026-10-21 à 21 h 03 UTC : 11 matchs, dont 4 avec Pinnacle. Descriptif, aucun seuil établi : Je ne sais pas ce qui serait « normal ».
- Anomalie de données : ce relevé est postérieur au coup d'envoi (19 h 00 UTC) des 6 matchs du 21/10 qu'il contient. La note du dossier (« à plus de 2 h du coup d'envoi ») est vraie pour les 5 matchs de novembre, pas pour ces 6. Les valeurs ne ressemblent pas à des cotes d'avant-match : probabilité moyenne du nul de 0,834 pour Bayern–Arsenal (28 bookmakers), de 0,916 pour la victoire de Betis face à Feyenoord (19), marge moyenne de 1,308 pour Brugge–Lens (3 bookmakers) et de 0,989 pour Real Madrid–Leipzig (4). Je ne sais pas ce que l'API renvoie pendant ou après le match.
  Les écarts Pinnacle moins moyenne des 4 matchs concernés (Bayern–Arsenal, Betis–Feyenoord, Inter–Shakhtar, Sporting–LASK) sortent de ce même relevé : à ne pas interpréter.
- Les 5 matchs de novembre (03/11 : Atlético–Bayern, Villarreal–PSG ; 04/11 : AEK–Real Madrid, Slavia–Arsenal, Porto–Napoli) ont 8 à 17 bookmakers, aucun avec Pinnacle, une marge moyenne de 0,091 à 0,279 selon le match, et un écart-type entre bookmakers de 0,003 à 0,055 sur les probabilités. Relevé pris 13 jours avant les premiers coups d'envoi, donc très vieux pour ce qu'il décrit.
- Écart-type moyen entre bookmakers sur les 11 matchs : 0,100 / 0,066 / 0,058 (domicile / nul / extérieur), mais il est tiré par les 6 matchs postérieurs au coup d'envoi.

### g. Pistes

1. Le désaccord entre bookmakers comme signal. Mesure : sur l'historique des championnats, regrouper les matchs par niveau de désaccord entre bookmakers (écart-type des probabilités sans marge) et mesurer si le log loss de la cote de clôture recalibrée est plus mauvais là où ils divergent, puis ajouter ce désaccord comme signal au banc (marché + un signal), même protocole que fb-H9 à fb-H14. Pourquoi : le dossier montre des écarts très variables d'un match à l'autre, mais ce relevé est abîmé (voir f), donc il ne prouve rien ; l'idée vient surtout de fb-H12 et fb-H13, déjà rejetées. Apport : faible, c'est un proche cousin de fb-H12 et fb-H13 sur un marché déjà très fort. Échec : intervalle centré sur zéro avec une borne haute sous 0,001, comme les six précédentes ; l'historique ne contient peut-être pas les cotes de chaque bookmaker (Je ne sais pas). Cette idée vient de résultats que j'ai vus (rejets fb-H12 et fb-H13) : elle ne peut être jugée que sur des matchs postérieurs au 2026-10-25, donc pas sur l'historique déjà utilisé par le banc.
2. Où l'écart plus/moins 2,5 buts dérivé se creuse. Mesure : sur les 5 553 matchs de `football_derive_2026-10-17`, découper l'écart de log loss entre le plus/moins dérivé du 1X2 et la vraie cote plus/moins selon la probabilité du favori au 1X2 (matchs équilibrés contre déséquilibrés). Pourquoi : l'écart global est de +0,0028 et la Ligue des champions oppose souvent des équipes de niveaux très différents ; le dossier ne dit pas où l'écart se concentre. Apport : un diagnostic de fb-H8, pas un moyen de battre le marché, puisque la vraie cote plus/moins reste la référence. Échec : écart homogène entre tranches, ou tranches de moins de 50 matchs, qui ne disent rien (§14). Cette idée vient de résultats déjà vus (le contrôle `derive-check`) : elle ne peut être jugée que sur des matchs postérieurs au 2026-10-25, et le carnet de la Ligue des champions (9 notés, 100 requis) n'en fournira pas assez avant des mois.

Questions pour Chris :
1. Le Mac est-il branché et réveillé les soirs de match ? 21 trous sur 22 datent d'après le 23/10 à 23 h 33 UTC, et le prochain gel doit tomber entre 18 h 00 et 19 h 59 UTC le 03/11 (matchs de 20 h 00 UTC). Qu'est-ce qui a changé sur le Mac depuis le 24/10 ?
2. Le relevé de cotes du 21/10 à 21 h 03 UTC est-il voulu (relevé en direct pendant les matchs) ? Si oui, faut-il que la section « structure du marché » du dossier ne retienne que des relevés d'avant le coup d'envoi ? C'est une décision de code, qui t'appartient.
3. Veux-tu archiver, dans la limite du plafond de 400 crédits (59 utilisés), les cotes bookmaker par bookmaker des championnats à partir de maintenant ? Sans cela, la piste 1 n'aurait aucune donnée postérieure au 2026-10-25 à juger.

