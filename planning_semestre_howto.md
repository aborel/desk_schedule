# Planning des guichets mode semestre (WORK IN PROGRESS)

## Onglet "jours"

Les jours sont lundi, mardi,... vendredi, numérotés à partir de lundi = zéro.


## Onglet "guichetiers"

Unité/taux/etc: dans les colonnes **à droite** du tableau (convenu avec GR). Le taux d'activité doit correspondre à une valeur définie dans la colonne A de l'onglet quotas (voir ci-dessous).


## Onglet "séances"

Contrôler que les définitions des séances de direction et d'unités sont correctes.


## Onglet "quotas"

Les quotas doivent avoir des valeurs pour tous les types de guichetiers (Colonne "Taux" de l'onglet guichetiers; en général c'est le taux d'activité mais il y a beaucoup d'autres types plus ou moins historiques), même si on ne les utilise pas par la suite.

Les valeurs des quotas sont en heures par semaine.


## Règles minimales pour un premier essai

Dans un premier temps, le programme doit trouver avec les règles suivantes (en ignorant tout quota), sinon cela indique un problème sérieux quelque part dans les données:

oneLibrarianPerShift
oneShiftAtATime
maxTwoShiftsPerDay

noOutOfTimeShift


Le résultat ne sera pas forcément équilibré. Si ça marche, on peut essayer de répartir un peu mieux en ajouter des contraintes de type quota:

maxActiveShifts

maxReserveShifts dans un 2ème temps

Les quotas max sont facilement respectés dans l'organisation en place depuis la fin du confinement. Par contre il n'y a plus assez de plages de guichet pour les quotas min définis avant 2020).

S'il manque des guichetiers pour une des plages de guichet (autre que le vendredi soir 18-20h), le modèle de planning n'aura pas de solution,
consulter la section "roster" du log pour savoir si c'est le cas. Si c'est un soir de 18-20h, on peut contourner le problème en ajoutant un guichetier fictif disponible juste pour la plage en question, mais la recherche d'une solution définitive risque d'être laborieuse.
