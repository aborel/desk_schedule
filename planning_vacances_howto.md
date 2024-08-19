# Planning des guichets mode vacances

## Onglet "jours"

Indiquer les dates de début et de fin dans generate_days_list.py et exécuter.
L'output (2 colonnes séparées par une tabulation) peut être collé directement dans Excel. Le jour est indiqué comme `JourDeLaSemaine JJ-MM-AAAA`
Les jours doivent être reportés à l'identique (copie transposée, comme lignes) dans les onglets "guichetiers" et "guichets".
Les jours fériés sont à enlever en dernier lieu.


## Onglet "guichetiers"

Unité/taux/etc: dans les colonnes **à droite** du tableau (convenu avec GR)

Le nom des guichetiers doit absolument être indiqué comme dans Absences v2. Selon les informations reçues de la DSI (INC0648134), la forme est le premier prénom suivi du nom de famille complet tiré des documents d'identité EPFL. C'est le standard de SAP, les noms d'usage qu'on peut avoir dans l'annuaire et/ou l'e-mail ne s'appliquent pas.


## Export des congés depuis Absences V2

https://absences2.epfl.ch

Planning composé de tout le SISB

Exporter comme "Page web, complète"

Problème: l'affichage du planning est fixé au mois en cours + 2 mois suivants => pas d'extraction juillet+août quand on est en mai. Conseil des de l'équipe Absences: on peut contourner en changeant la date courante dans le navigateur avec une extension comme Time Travel pour Chrome https://chromewebstore.google.com/detail/time-travel/jfdbpgcmmenmelcghpbbkldkcfiejcjg 

Problème2: les absences pour cause de vacances ne sont plus différenciées dans autres pour raison de protection des données. Mais on peut au moins filtrer le télétravail qui doit être ignoré pour ces périodes de vacances

1. le module Python parse_absences est appelé automatiquement quand on donne en input un fichier HTML d'absences + la règle `useAbsences` dans l'input XLSX. lit le fichier HTML et produit un fichier vacation.json contenant les jours d'absences de tout le personnel sous la forme `[{'Nom1 Prénom1': [["(début absence1", "fin absence1"], ["début absenc2", "fin absence2"]...]...}]`
Les dates sont au format ISO `YYYY-MM-DD`.
2. Matching des jours de l'export Absences et du fichier Excel: dans `or_librarydesk_schedule.py` à partir de lignes ci-dessous. La fonction `datetime.parse()` interprète confortablement toutes sortes de formats pour créer des objets `datetime` qu'on peut ensuite comparer, transformer, etc.

```
    for n in all_librarians:
        for d in all_days:
            desk_day = dateparser.parse(weekdays[d])
```

## Règles minimales pour un premier essai

Dans un premier temps, le programme doit trouver avec les règles suivantes (en ignorant tout quota), sinon cela indique un problème sérieux quelque part dans les données:

oneLibrarianPerShift
oneShiftAtATime
maxTwoShiftsPerDay

noOutOfTimeShift

useAbsences

Le résultat ne sera pas équilibré du tout. Si ça marche, on peut essayer de répartir un peu mieux en ajouter des contraintes de type quota:

maxActiveShifts
ScaleQuotas (indispensable si on a plus de 1-2 semaines!)

maxReserveShifts dans un 2ème temps