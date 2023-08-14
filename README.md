
# Homer Personality Ontology

## Context

This project is part of a semantic web course initiative, focusing on the analysis of various texts. The chosen text for this project is the "Odyssey" by Homer.

## Objectives

The project's objectives are structured into four distinct steps:

1. Convert the initial file (`./etape_1/hom.od_eng.xml`) into a `.json` format.
2. Disambiguate the texts using [pywsd](https://github.com/alvations/pywsd).
3. Compare the disambiguation results with data in [OntoSenticNet](https://sentic.net/ontosenticnet.zip).
4. Perform an ontological alignment between the project data and [LemonUby](https://lemon-model.net/lexica/uby/wn/wn.nt.gz).

## Development and Procedure

The project is divided into four steps, each with specific tasks:

#### Step 1 - Conversion

Convert the file `./etape_1/hom.od_eng.xml` to `./etape_1/hom.od_eng.json` using the [xmltodict] library.

#### Step 2 - Disambiguation

The text was cleaned to remove special characters that were not encoded correctly. The `milestones` and `locations` XML tags were also removed. The file was then restructured to retain only relevant elements. Disambiguation was performed using [pywsd](https://github.com/alvations/pywsd) and [nltk](https://www.nltk.org/).

#### Step 3 - Alignment with OntoSenticNet

The synsets obtained from the previous step were used to find the most similar concept in [OntoSenticNet](https://sentic.net/ontosenticnet.zip) using [Fuseki](https://jena.apache.org/documentation/fuseki2/). The output provides information about the word's synset, concept, and associated sentics.

#### Step 4 - Ontological Alignment

The ontological alignment was achieved using the [Lemon](https://lemon-model.net/index.php) ontology. Two alignment methods were explored:

1. A direct alignment inspired by LemonUby's structure.
2. A triplet-based alignment, with three variations of the alignment file.

## Results and Conclusion

The developed codes produce results that align with the project's objectives. The project is designed as a pipeline, allowing for easy processing of properly formatted input data.

