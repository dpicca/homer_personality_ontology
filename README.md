# Plato_Homer_Personality

## Context

In the context of the course on the semantic web given by Davide Picca, we were asked to analyze several texts at the rate of one text per person. I therefore focused on the Odyssey by Homer.

## Objectives

The objectives of the project are simple and can be divided into four distinct steps

- Convert the starting file ([./etape_1/hom.od_eng.xml](./etape_1/hom.od_eng.xml)) into a `.json` file.
- Disambiguate the texts with [pywsd](https://github.com/alvations/pywsd)
- Compare the results of the disambiguation with the data in [OntoSenticNet](https://sentic.net/ontosenticnet.zip)
- Do an ontological alignment between our data and [LemonUby](https://lemon-model.net/lexica/uby/wn/wn.nt.gz)

## Development and procedure

As mentioned in the previous point, the project consists of four steps which I will describe in more detail here.

#### Step 1 - conversion

The first step is simple: convert the file [./etape_1/hom.od_eng.xml](./etape_1/hom.od_eng.xml) to [./etape_1/hom.od_eng.json](./etape_1/hom.od_eng.json). Using the [xmltodict] library (pypi.org/project/xmltodict) allows us to do this automatically.

#### Step 2 - disambiguation

This step required more work than initially expected. Indeed, I spent some time to clean the file [./etape_1/hom.og_eng.xml](./etape_1/hom.og_eng.xml) of all the special characters that were not encoded correctly. To make it simple: some characters were not encoded correctly and disappeared when converted with _xmltodict_. This would not have been a problem if the conversion left a space in place of the character, but it did not. It concatenated the words on either side of the character: "Ethiopians&mdash;the Ethiopians" became "Ethiopiansthe Ethiopians" because the encoded character was not recognized by the conversion.

I also removed the `milestones`, an xml tag that informed the page numbers, as well as the `locations`, an xml tag that encapsulated words that referred to existing places. The reason? The same reason as for the special characters: the conversion was concatenating the words.

Finally, I restructured the [./etape_1/hom.od_eng.json](./etape_1/hom.od_eng.json) file and thus created [./etape_2/restructured_data.json](./etape_2/restructured_data.json) to keep only the elements that were useful for the following. The code that produced this result was written in [./etape_2/restructure.py](./etape_2/restructure.py).

For the actual disambiguation, I used [pywsd](https://github.com/alvations/pywsd) as well as [nltk](https://www.nltk.org/). The process was simple: separate the texts into sentences with _nltk_ (this made the code run 4 to 5 times faster) and then disambiguate these sentences with the `disambiguate` function of _pywsd_. This function uses an algorythm named `max_similarity` which caused quite a few problems before simply being modified as described in this [issue on GitHub](https://github.com/alvations/pywsd/issues/59). Once the problem is fixed, the program runs smoothly and returns a list of objects that look like `["Muse", "muse", "muse.n.02"]` where the first element is the original word as it is in the text, the second element is the lemma of the word, and the third is the [synset](https://wordnet.princeton.edu/) of the word. The result is obtained in the file [./etape_2/diambiguate.py](./etape_2/diambiguate.py)

#### Step 3 - alignment with OntoSenticNet

I won't go into the details of what OntoSenticNet is, to understand the general structure you can refer to [this file](https://sentic.net/ontosenticnet.pdf). The idea is again quite simple: for each synset obtained in step 2 we want to search on [OntoSenticNet](https://sentic.net/ontosenticnet.zip), by interacting with [Fuseki](https://jena.apache.org/documentation/fuseki2/), the concept, or `semantic`, that best corresponds to it. Once this work is done, it only remains to retrieve the `sentics` of the most similar concept and compile the whole in a dictionary.

Concretely, the code ([./etape_3/ontoSenticNet_analysis.py]) does exactly that:

- We start from the synsets of [./etape_2/diambiguate.py](./etape_2/diambiguate.py)
- For each synset we :
  - Retrieve the concepts in OntoSenticNet
  - Retrieve the synsets of these concepts
  - Calculate the similarity (with the `wup_similarity` function of _nltk wordnet_) between the starting synset and the synsets of OntoSenticNet concepts
  - Returns the most similar concept
- For each selected concept, we retrieve the corresponding synsets
- We prepare the output

There are one or two subtleties like the [SPARQL] queries (https://www.w3.org/TR/rdf-sparql-query/), or the fact that I decided not to keep the synsets whose most similar concept had a similarity rate of 0%. But in the end, nothing very complex.

The final file, [./etape_3/hom.od_eng_OntoSenticNet_analysis.json](./etape_3/hom.od_eng_OntoSenticNet_analysis.json), fills in information with the following structure:

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

#### Step 4 - ontological alignment

The ontological alignment was both simple and complicated. The complexity came from the little theory I had been exposed to. In the end it is extremely simple: [Lemon](https://lemon-model.net/index.php) is an ontology for describing lexicons. LemonUby](https://lemon-model.net/lexica/uby/modelling.php) provides synsets (result of an ontological alignment between WordNet and Lemon). So, we "just" had to align our data with [LemonUby - WordNet](https://lemon-model.net/lexica/uby/wn/wn.nt.gz).

I realized two codes:

##### 1: [./etape_4/ontology_alignment_rdf.py](./etape_4/ontology_alignment_rdf.py)

This file allowed me to obtain [./etape_4/aligned_ontologies.rdf](./etape_4/aligned_ontologies.rdf). This file proposes a rather simple ontological alignment inspired by the structure of LemonUby's [modelling](https://lemon-model.net/lexica/uby/modelling.php):

```xml
<lemon:LexicalSense rdf:about="WN_Sense_573">
   <uby:monolingualExternalRef>
     <uby:externalReference>[POS: noun] cat%1:06:00::</uby:externalReference>
     <uby:externalSystem>Wordnet 3.0 part of speech and sense key</uby:externalSystem>
   </uby:monolingualExternalRef>
</lemon:LexicalSense>
```

then becomes:

```xml
<lemon:LexicalSense rdf:about="WN_Sense_48086">
  <ontosenticnet:concept>commonwealth</ontosenticnet:concept>
  <ontosenticnet:sensitivity>0</ontosenticnet:sensitivity>
  <ontosenticnet:aptitude>0.647</ontosenticnet:aptitude>
  <ontosenticnet:attention>-0.51</ontosenticnet:attention>
  <ontosenticnet:pleasantness>0.716</ontosenticnet:pleasantness>
</lemon:LexicalSense>
```

So, as long as we search for the same "WN*Sense*###", we will find the information from LemonUby and our data.

##### 2. [./etape_4/ontology_alignment_nt.py](./etape_4/ontology_alignment_nt.py)

This file allowed me to create the three `.nt` files. Short description of these:

1. [./etape_4/aligned_ontologies.nt](./etape_4/aligned_ontologies.nt). Based on a triplet logic, this file proposes the closest ontological alignment to LemonUby. Indeed, each triplet starts with the reference of the word in LemonUby, then it continues with the corresponding element in OntoSenticNet, to finish on the value of this element. It is obtained by using the `updateGraph()` function.
2. [./stage*4/aligned_ontologies*(includes_owl_same_as).nt](<./stage_4/aligned_ontologies_(includes_owl_same_as).nt>). Still based on the triplet logic, this one offers a slightly different version: the LemonUby information appears only once. Let me explain. Each triplet that starts with a reference to LemonUby continues with a `owl:sameAs` and is ended by the reference to the OntoSenticNet concept. It only remains to write triples that give information about these OntoSenticNet concepts. This file is obtained with the `updateGraph_including_sameAs()` function.
3. [./etape*4/aligned_ontologies*(only_owl_same_as).nt](<./etape_4/aligned_ontologies_(only_owl_same_as).nt>). Simplest version: only references are made between OntoSenticNet data and LemonUby data. Each triplet is composed of the LemonUby reference, then followed by a `owl:sameAs`, and is terminated by the reference in OntoSenticNet. This version is more general because it doesn't fill in any specific data (or at least no specific data that we would have retrieved before) except the references themselves. This file is obtained with the function `updateGraph_sameAs_only()`.

## Results and conclusion

The codes produced during the realization of this project lead to results that seem correct. I admit that I did not test the ontological alignments myself, but in principle everything should work. It is also interesting to note that all the files obtained from this project are potential candidates for the title of "successful work". What I mean by that is that all these results have different methodologies, different approaches, and therefore different results. Another point that I think is important to emphasize is that this project is set up like a pipeline: as long as you have starting data that are properly formatted, you just have to run the codes after each other. 
