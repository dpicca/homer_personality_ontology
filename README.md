# Plato_Homer_Personality

## Contexte

Dans le cadre du cours sur le web sémantique donné par Davide Picca, il nous a été demandé d'analyser plusieurs textes à raison d'un texte par personne. Je me suis dès lors concentré sur l'Odyssée par Homère.

## Objectifs

Les objectifs du projet sont simples et divisibles en quatre étapes distinctes:

- Convertir le fichier de départ ([./etape_1/hom.od_eng.xml](./etape_1/hom.od_eng.xml)) en fichier `.json`.
- Désambiguiser les textes avec [pywsd](https://github.com/alvations/pywsd)
- Comparer les résultats de la désambiguisation avec les données de [OntoSenticNet](https://sentic.net/ontosenticnet.zip)
- Faire un alignement ontologique entre nos données et [LemonUby](https://lemon-model.net/lexica/uby/wn/wn.nt.gz)

## Développement et procédure

Comme mentionné au point précédant, le projet se compose de quatre étapes que je vais décrire plus en détail ici.

#### Etape 1 - conversion

L'étape une est simple : il s'agit de convertir le fichier [./etape_1/hom.od_eng.xml](./etape_1/hom.od_eng.xml) pour obtenir [./etape_1/hom.od_eng.json](./etape_1/hom.od_eng.json). L'utilisation de la librairie [xmltodict](pypi.org/project/xmltodict) nous permet de le faire automatiquement.

#### Etape 2 - désambiguisation

Cette étape a nécessité plus de travail que ce qui était initialement attendu. En effet, j'ai passé un moment à nettoyer le fichier [./etape_1/hom.og_eng.xml](./etape_1/hom.og_eng.xml) de tous les caractères spéciaux qui n'étaient pas encodés correctement. Pour faire simple : certains caractères n'étaient pas encodés correctement et disparaissaient lors de la conversion avec _xmltodict_. Ça n'aurait pas été un problème si la conversion laissait un espace en lieu et place du caractère, mais ce n'était pas le cas. Elle concaténait les mots qui se trouvaient d'une part et d'autre du caractère : "Ethiopians&mdash;the Ethiopians" devenait "Ethiopiansthe Ethiopians" car le caractère encodé n'était pas reconnu par la conversion.

J'ai aussi retiré les `milestones`, une balise xml qui renseignait les numéros de pages, ainsi que les `locations`, une balise xml qui encapsulait les mots qui faisaient référence à des lieux existants. La raison ? La même que pour les caractères spéciaux : la conversion concaténaitles mots.

Enfin, j'ai restructuré le fichier [./etape_1/hom.od_eng.json](./etape_1/hom.od_eng.json) et ai ainsi créé [./etape_2/restructured_data.json](./etape_2/restructured_data.json) pour ne garder que les éléments utiles à la suite. Le code qui a produit ce résultat a été écrit dans [./etape_2/restructure.py](./etape_2/restructure.py).

Pour la désambiguisation à proprement parler, j'ai fait appel à [pywsd](https://github.com/alvations/pywsd) ainsi qu'à [nltk](https://www.nltk.org/). Le processus était simple : séparer les textes en phrases avec _nltk_ (cela rendait l'exécution du code 4 à 5 fois plus rapide) puis désambiguiser ces phrases avec la fonction `disambiguate` de _pywsd_. Cette fonction utilise un algorythme nommé `max_similarity` qui a causé pas mal de problèmes avant de simplement être modifié comme décrit dans cette [issue sur GitHub](https://github.com/alvations/pywsd/issues/59). Une fois le problème réglé, le programme tourne sans problème et nous retourne une liste d'objets qui ressemblent à `["Muse", "muse", "muse.n.02"]` où le premier élément est le mot d'origine tel qu'il est dans le texte, le deuxième élément est le lemme du mot, et le troisième est le [synset](https://wordnet.princeton.edu/) du mot. Le résultat est obtenu dans le fichier [./etape_2/diambiguate.py](./etape_2/diambiguate.py)

#### Etape 3 - alignement avec OntoSenticNet

Je n'entrerai pas dans les détails de ce qu'est OntoSenticNet, pour comprendre la structure générale, vous pouvez vous référer à [ce fichier](https://sentic.net/ontosenticnet.pdf). L'idée est à nouveau assez simple : pour chaque synset obtenu à l'étape 2 on souhaite chercher sur [OntoSenticNet](https://sentic.net/ontosenticnet.zip), en interagissant avec [Fuseki](https://jena.apache.org/documentation/fuseki2/), le concept, ou `semantic`, qui lui correspond le mieux. Une fois ce travail achevé, il ne reste plus qu'à récupérer les `sentics` du concept le plus similaire et compiler le tout dans un dictionnaire.

Concrètement, le code ([./etape_3/ontoSenticNet_analysis.py](./etape_3/ontoSenticNet_analysis.py)) fait exactement ça:

- On part des synsets de [./etape_2/diambiguate.py](./etape_2/diambiguate.py)
- Pour chaque synset on :
  - Récupère les concepts dans OntoSenticNet
  - Récupère les synsets de ces concepts
  - Calcule la similarité (avec la fonction `wup_similarity` de _nltk wordnet_) entre le synset de départ et les synsets des concepts OntoSenticNet
  - Retourne le concept le plus similaire
- Pour chaque concept retenu on récupère les sentics correspondants
- On prépare l'output

Il y a une ou deux subtilités comme les query [SPARQL](https://www.w3.org/TR/rdf-sparql-query/), ou le fait que j'aie décidé de ne pas garder les synsets dont le concept le plus similaire avait un taux de similarité égal à 0%. Mais au final, rien de bien complexe.

Le fichier final, [./etape_3/hom.od_eng_OntoSenticNet_analysis.json](./etape_3/hom.od_eng_OntoSenticNet_analysis.json), renseigne les informations avec la structure suivante:

```json
{
  "word": "muse.n.02",
  "concept": "goddess",
  "sensitivity": "0",
  "aptitude": "0.887",
  "attention": "0",
  "pleasantness": "0.958"
}
```

#### Etape 4 - alignement ontologique

L'alignement ontologique fut à la fois simple et compliqué. La complexité provenait notamment du peu de théorie à laquelle j'avais pu (m')être exposé. Au final c'est extrêment simple : [Lemon](https://lemon-model.net/index.php) est une ontologie pour décrire des lexiques. [LemonUby](https://lemon-model.net/lexica/uby/modelling.php) renseigne les synsets (résultat d'un alignement ontologique entre WordNet et Lemon). Ainsi, il fallait "juste" aligner nos données avec celle de [LemonUby - WordNet](https://lemon-model.net/lexica/uby/wn/wn.nt.gz).

J'ai réalisé deux code:

##### 1: [./etape_4/ontology_alignment_rdf.py](./etape_4/ontology_alignment_rdf.py)

Ce fichier m'a permis d'obtenir [./etape_4/aligned_ontologies.rdf](./etape_4/aligned_ontologies.rdf). Ce fichier propose un alignement ontologique assez simple inspiré de la structure du [modelling](https://lemon-model.net/lexica/uby/modelling.php) de LemonUby:

```xml
<lemon:LexicalSense rdf:about="WN_Sense_573">
   <uby:monolingualExternalRef>
     <uby:externalReference>[POS: noun] cat%1:06:00::</uby:externalReference>
     <uby:externalSystem>Wordnet 3.0 part of speech and sense key</uby:externalSystem>
   </uby:monolingualExternalRef>
</lemon:LexicalSense>
```

devient alors:

```xml
<lemon:LexicalSense rdf:about="WN_Sense_48086">
  <ontosenticnet:concept>commonwealth</ontosenticnet:concept>
  <ontosenticnet:sensitivity>0</ontosenticnet:sensitivity>
  <ontosenticnet:aptitude>0.647</ontosenticnet:aptitude>
  <ontosenticnet:attention>-0.51</ontosenticnet:attention>
  <ontosenticnet:pleasantness>0.716</ontosenticnet:pleasantness>
</lemon:LexicalSense>
```

Ainsi, du moment qu'on recherche le même "WN*Sense*###", on trouvera les informations de LemonUby et de nos données.

##### 2. [./etape_4/ontology_alignment_nt.py](./etape_4/ontology_alignment_nt.py)

Ce fichier m'a permis de créer les trois fichiers `.nt`. Petite description rapide de ceux-ci:

1. [./etape_4/aligned_ontologies.nt](./etape_4/aligned_ontologies.nt). Basé sur une logique de triplets, ce fichier propose l'alignement ontologique le plus proche de LemonUby. En effet, chaque triplet commence par la référence du mot dans LemonUby, puis il continue avec l'élément correspondant dans OntoSenticNet, pour finir sur la valeur de cet élément. Il est obtenu en utilisant la fonction `updateGraph()`.
2. [./etape*4/aligned_ontologies*(includes_owl_same_as).nt](<./etape_4/aligned_ontologies_(includes_owl_same_as).nt>). Toujours basé sur la logique de triplets, celui-ci propose une version légèrement différente : les information de LemonUby n'apparaissent qu'une fois. Je m'explique. Chaque triplet qui commence par une référence à LemonUby se continue par un `owl:sameAs` et est terminé par la référence vers le concept OntoSenticNet. Il ne reste alors plus qu'à écrire des triplets qui renseignent les informations relatives à ces concepts OntoSenticNet. Ce fichier est obtenu avec la fonction `updateGraph_including_sameAs()`.
3. [./etape*4/aligned_ontologies*(only_owl_same_as).nt](<./etape_4/aligned_ontologies_(only_owl_same_as).nt>). Version la plus simple : on ne fait que des références entre les données d'OntoSenticNet et celles de LemonUby. Chaque triplet est composé de la référence LemonUby, puis est suivi par un `owl:sameAs`, et est terminé par la référence dans OntoSenticNet. Cette version est plus générale car elle ne renseigne pas de données précises (ou du moins pas de données précises qu'on aurait récupéré auparavant) à part les références elles-mêmes. Ce fichier est obtenu avec la fonction `updateGraph_sameAs_only()`.

## Résultats et conclusion

Les codes produits lors de la réalisation de ce projet amènent à des résultats qui semblent corrects. J'avoue ne pas avoir testé moi-même les alignements ontologiques, mais en principe tout devrait fonctionner. Il est intéressant de noter aussi que tous les fichiers obtenus à l'issue de ce projet sont des candidats potentiels pour le titre de "travail réussi". Ce que j'entend par là c'est que tous ces résultats présentent des méthodologies différentes, des approches différentes, et, du coup, des résultats différents. Un autre point qu'il me semble important de souligner est que ce projet est constitué comme une pipeline : du moment qu'on a des données de départ qui sont formatées correctement, il suffit d'exécuter les codes les uns après les autres pour arriver au résultat final.

Pour résumer, tous les fichiers de résultats créent un alignement qui lie les données de cette façon :
Concept LemonUby -> informations dans OntoSenticNet.

Spécifiquement :

- [./etape_4/aligned_ontologies.rdf](./etape_4/aligned_ontologies.rdf) : suivant la structure Lemon, on remplace les données de lemon (notamment `uby:monolingualExternalRef`) par les données prises d'OntoSenticNet.
- [./etape_4/aligned_ontologies.nt](./etape_4/aligned_ontologies.nt) : comme décrit dans le read.me de Simon Cappelle, cet alignement ontologique prend la forme de n-triples qui lient directement les données LemonUby avec les données OntoSenticNet.
- [./etape*4/aligned_ontologies*(includes_owl_same_as).nt](<./etape_4/aligned_ontologies_(includes_owl_same_as).nt>) : la seule différence avec le fichier précédent est que les données LemonUby sont d'abord mises en rapport avec les concepts OntoSenticNets via la commande `owl:sameAs`, et les données récupérées sur OntoSenticNet sont mises en relation avec les concepts eux-mêmes.
- [./etape*4/aligned_ontologies*(only_owl_same_as).nt](<./etape_4/aligned_ontologies_(only_owl_same_as).nt>) : version simplifiée du point précédant, ce code ne possède que les instruction `owl:sameAs`. De fait, les données récupérées sur OntoSenticNet ne sont pas présentes, puisque l'idée de ce fichier est de pointer, à partir d'un concept OntoSenticNet ou d'un objet Lemon:LexicalSense, vers les données correspondantes dans l'autre ontologie.

Il est difficile de tirer des conclusions d'un projet comme celui-ci, ne serait-ce que parce qu'il est difficile de prendre conscience de son utilité scientifique. À l'inverse, je dirais qu'il m'a permis d'en savoir plus sur le web sémantique et sur les ontologies d'un point de vue pédagogique. Mon expérience dans ce projet m'a notamment appris que la modélisation était une étape d'une importance capitale pour le bon développement de la pipeline.
