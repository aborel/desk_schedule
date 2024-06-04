# Planning des guichets mode semestre (WORK IN PROGRESS)

## Onglet "jours"

Les jours sont lundi, mardi,... vendredi, numérotés à partir de lundi = zéro.


## Onglet "guichetiers"

Unité/taux/etc: dans les colonnes **à droite** du tableau (convenu avec GR)



## Règles minimales pour un premier essai

Dans un premier temps, le programme doit trouver avec les règles suivantes (en ignorant tout quota), sinon cela indique un problème sérieux quelque part dans les données:

oneLibrarianPerShift
oneShiftAtATime
maxTwoShiftsPerDay

noOutOfTimeShift


Le résultat ne sera pas forcément équilibré. Si ça marche, on peut essayer de répartir un peu mieux en ajouter des contraintes de type quota:

maxActiveShifts

maxReserveShifts dans un 2ème temps