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

L'étape une est simple : il s'agit de convertir le fichier [./etape_1/hom.od_eng.xml](./etape_1/hom.od_eng.xml) pour obtenir [./etape_1/hom.od_eng.json](./etape_1/hom.od_eng.json). L'utilisation de la librairie [xmltodict](pypi.org/project/xmltodict) nous permet de le faire automatiquement.

### Etape 2 - désambiguisation

Cette étape a nécessité plus de travail que ce qui était initiallement attendu. En effet, j'ai passé un moment pour nettoyer de fichier [./etape_1/hom.og_eng.xml](./etape_1/hom.og_eng.xml) de tous les caractère spéciaux qui n'étaient pas encodés correctement. Pour faire simple : certain caractère n'étaient pas encodé correctement et, lors de la conversion avec _xmltodict_, disparaissaient. Ça n'aurait pas été un problème si la conversion laissait un espace en lieu et place du caractère, mais ce n'était pas le cas. Elle concaténait les mots qui se trouvaient d'une part et d'autre du caractère : "Ethiopians&mdash;the Ethiopians" devenait "Ethiopiansthe Ethiopians" car le caractère encodé n'était pas reconnu par la conversion.

J'ai aussi retiré les `milestones`, une balise xml qui renseignait les numéros de pages, ainsi que les `locations`, une balise xml qui encaplusait les mots qui faisaient référence à des lieux existants. La raison ? La même que pour les caractère spéciaux : la conversion concaténait les mots.

Enfin, j'ai restructuré le fichier [./etape_1/hom.od_eng.json](./etape_1/hom.od_eng.json) et a ainsi créé [./etape_2/restructured_data.json](./etape_2/restructured_data.json) pour ne garder que les éléments utiles à la suite. Le code qui a produit se résultat se trouve à [./etape_2/restructure.py](./etape_2/restructure.py).

Pour la désambiguisation à proprement parler, j'ai fait appel à [pywsd](https://github.com/alvations/pywsd) ainsi qu'à [nltk](https://www.nltk.org/). Le processus était simple : séparer les textes en phrases avec _nltk_ puis désambiguiser ces phrases avec la fonction `disambiguate` de _pywsd_. Cette fonction utilise un algorythme nommée `max_similarity` qui a posé pas mal de problèmes avant de simplement être modifié comme décrit dans cette [issue sur GitHub](https://github.com/alvations/pywsd/issues/59). Une fois le problème réglé, le programme tourne sans problème et nous retourne une liste d'objets qui ressemblent à `["Muse", "muse", "muse.n.02"]` où le premier élément est le mot d'origine tel qu'il est dans le texte, le deuxième élément est le lemme du mot, et le troisième est le [synset](https://wordnet.princeton.edu/) du mot. Le résultat est obtenu sous la forme du fichier [./etape_2/diambiguate.py](./etape_2/diambiguate.py)

### Etape 3 - alignement avec OntoSenticNet

Je n'entrerai pas dans les détails de ce qu'est OntoSenticNet, pour comprendre la structure générale, vous pouvez vour référer à [ce fichier](https://sentic.net/ontosenticnet.pdf). L'idée est à nouveau assez simple : pour chaque synset obtenu à l'étape 2 on souhaite chercher sur [OntoSenticNet](https://sentic.net/ontosenticnet.zip), en interagissant avec [Fuseki](https://jena.apache.org/documentation/fuseki2/), le concept, ou `semantic`, qui lui correspond le mieux. Une fois ce travail achevé, il ne reste plus qu'à récupérer les `sentics` du concept le plus similaire et compiler le tout dans un dictionnaire.

Concrétement, le code ([./etape_3/ontoSenticNet_analysis.py](./etape_3/ontoSenticNet_analysis.py)) fait exactement ça:

- On part des synsets de [./etape_2/diambiguate.py](./etape_2/diambiguate.py)
- Pour chaque synset on :
  - Récupère les concepts dans OntoSenticNet
  - Récupère les synsets de ces concepts
  - Calcule la similarité (avec la fonction `wup_similarity` de _nltk wordnet_) entre le synset de départ et les synsets des concepts OntoSenticNet
  - Retourne le concept le plus similaire
- Pour chaque concept on récupère les sentics correspondants
- On prépare l'output

Il y a une ou deux subtilités comme les query [SPARQL](https://www.w3.org/TR/rdf-sparql-query/), ou le fait que j'aie décidé de ne par garder les synsets dont le concept le plus similaire avait un taux de similarité égal à 0%. Mais au final, rien de bien complexe.

Le fichier final, [./etape_3/hom.od_eng_OntoSenticNet_analysis.py](./etape_3/hom.od_eng_OntoSenticNet_analysis.py), renseigne les informations suivant la structure suivante:

````json
{
  "word": "muse.n.02",
  "concept": "goddess",
  "sensitivity": "0",
  "aptitude": "0.887",
  "attention": "0",
  "pleasantness": "0.958"
}
```

### Etape 4 - alignement ontologique

résultats et conclusion
````
