# Plato_Homer_Personality

## Contexte

Dans le cadre du cours sur le web sémantique donnée par Davide Picca, il nous a été demandé de d'analyser plusieurs textes à raison d'un texte par personne. J'ai eu droit à l'Odyssée par Homère.

## Objectifs

Les objectif du projet sont simples et divisibles en quatre étapes distinctes:

- Convertir le fichier de départ (`./etape_1/hom.od_eng.xml`) en fichier `.json`.
- Désambiguiser les textes
- Comparer les résultats de la désambiguisation avec les données de OntoSenticNet
- Faire un alignement ontologique entre nos données et LemonUby

## Développement et procédure

Comme mentionné au point précédant, le projet se compose de quatre étapes qui je vais décrire plus en détail ici.

### Etape 1 - conversion

L'étape une est simple : il s'agit de convertir le fichier [./etape_1/hom.od_eng.xml](https://gitlab.com/ish_unil/students_sw/plato_homer_personality/-/blob/Loris_Rimaz/etape_1/hom.od_eng.xml) pour obtenir `./etape_1/hom.od_eng.json`. L'utilisation de la librairie [xmltodict](pypi.org/project/xmltodict) nous permet de le faire automatiquement.

### Etape 2 - désambiguisation

Cette étape a nécessité plus de travail que ce qui était initiallement attendu. En effet, j'ai passé un moment pour nettoyer de fichier `./etape_1/hom.og_eng.xml` de tous les caractère spéciaux qui n'étaient pas encodés correctement. Pour faire simple : certain caractère n'étaient pas encodé correctement et, lors de la conversion avec _xmltodict_, disparaissaient. Ça n'aurait pas été un problème si la conversion laissait un espace en lieu et place du caractère, mais ce n'était pas le cas : elle concaténait les mots qui se trouvaient d'une part et d'autre du caractère : "Ethiopians/mdash;the Ethiopians" devenait "Ethiopiansthe Ethiopians".
J'ai aussi retiré les `milestones`, une balise xml qui renseignait les numéros de pages, ainsi que les `locations`, une balise xml qui encaplusait les mots qui faisaient référence à des lieux existants. La raison ? La même que pour les caractère spéciaux : la conversion concaténait les mots.
Enfin, j'ai restructuré le `./etape_1/hom.od_eng.json` en `./etape_2/restructured_data.json` pour ne garder que les éléments utiles à la suite.

résultats et conclusion
