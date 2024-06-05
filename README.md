# Library Desk Scheduler

Basé sur les Google OR-Tools https://developers.google.com/optimization

Génération de planning des guichers sous contraintes.

A. Borel 2021-2024


# Rapport d'expérience oct. 2022 (on a progressé depuis)
Globalement, le programme fonctionne et donne des résultats satisfaisants, mais il n’est pas encore facilement utilisable par un non-développeur. En particulier, chaque nouvelle période de planning a impliqué quelques heures de retouche des données et d’analyse/débuggage avant de parvenir à un planning qui ne contienne pas d’erreur flagrante (résultat «passable» selon le résumé des opérations ci-dessus).
Pour que l’approche devienne réellement intéressante, il faudrait:
    1. standardiser une bonne fois pour toute le format du tableau de déclaration des disponibilités pour le guichet (aussi bien pour les semestres que pour les périodes de vacances universitaires) ;
    OK 2024
    2. améliorer le programme en termes de diagnostic: permettre d’avoir des informations sur les éventuels problèmes d’exécution sans devoir intervenir dans le code (réalisable en prinicipe à l’aide d’un fichier de log);
    Update 2024: légers progrès, les erreurs sont enregistrées dans un log spécifique
    3. former une personne à la bonne utilisation du logiciel (avec participation à la mise au point du fichier de log)
    Update 2024: un guide de base pour la génération d'un planning en mode semestre ou vacances est inclus (`planning_semestre_howto.md  et `planning_vacances_howto.md`)
    4. créer une version facilement déployable sur n’importe quel poste de travail (devrait être assez simple en utilisant la méthode conçue pour l’application acouachecksum).

# Nouveautés mai 2023
- Mini interface graphique (inspirée d'acouachecksum)
- Importation des données de vacances d'Absences V2 pour les périodes d'été et de Noël

# Données de base

Les fichiers de données utilisés sont dans V:/K_Guichets/K2_Guichets_physiques/K2.04_Planification_tournus/K2.043_Projections_Scenarii . Il s'agit de données personnelles qui n'ont pas leur place dans un dépôt public.