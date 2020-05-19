"""
ETAPE 4: alignement ontologique entre LemonUby et OntoSentic net.
    b) outputs en .nt
"""

import json
from SPARQLWrapper import SPARQLWrapper
from nltk.corpus import wordnet as wn
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, XSD

# Variables globales
INPUT_PATH = '../etape_3/hom.od_eng_OntoSenticNet_analysis'
INPUT_FORMAT = '.json'
with open(INPUT_PATH + INPUT_FORMAT, 'r') as input_file:
    DATA = json.load(input_file)

SPARQL = SPARQLWrapper(
    endpoint='http://localhost:3030/LemonUby/sparql', returnFormat='json'
)

OUTPUT_FORMAT = ".nt"

GRAPH = Graph()


def main():
    """
    Convertir les synsets pour en récupérer la "sense key" et
    Exporter les données en .nt
    """
    texts_words = DATA.get('analyse_ontoSenticNet')

    # Conversion des synsets en "sense keys"
    synsets = [{
        "synset": wn.synset(word["word"]).lemmas()[0].key(),
        "concept": word["concept"],
        "sensitivity": word["sensitivity"],
        "aptitude": word["aptitude"],
        "attention": word["attention"],
        "pleasantness": word["pleasantness"],
    } for words in texts_words.values() for word in words]

    # Création de l'alignement ontologique et création de l'output
    for synset in synsets:
        synset["synset"] = queryLemonUby(synset["synset"])
        updateGraph(synset)

    # Exporter le graph en .nt
    GRAPH.serialize(destination="aligned_ontologies" +
                    OUTPUT_FORMAT, format="nt")


def queryLemonUby(synset):
    """
    Interroger LemonUby pour récupérer le WN_Sense_## qui correspond au synset dans notre dataset
    """
    synset_type = synset.split("%")[1][0]
    query = """
        SELECT *
        WHERE {
           ?ref <http://purl.org/olia/ubyCat.owl#externalReference> "[POS: %s] %s".
        }
    """ % (getType(synset_type), synset)
    SPARQL.setQuery(query)
    try:
        result = SPARQL.query().convert()
        reference = result.get("results").get("bindings")[0].get("ref")
        # Retourner le WN_Sense_## avec les données URI
        return reference.get("value").split("#")[0]
    except:
        print("Something went wrong!")
        return


def updateGraph(synset):
    """
    Fonction pour obtenir le fichier "aligned_ontologies.nt"
    """
    lemon = URIRef(synset["synset"])
    urn = Namespace("urn:absolute:ontosenticnet#")

    GRAPH.add((lemon, urn.text, Literal(
        synset["concept"])))
    GRAPH.add((lemon, urn.pleasantness, Literal(
        synset["pleasantness"], datatype=XSD.decimal)))
    GRAPH.add((lemon, urn.attention, Literal(
        synset["attention"], datatype=XSD.decimal)))
    GRAPH.add((lemon, urn.sensitivity, Literal(
        synset["sensitivity"], datatype=XSD.decimal)))
    GRAPH.add((lemon, urn.aptitude, Literal(
        synset["aptitude"], datatype=XSD.decimal)))


def updateGraph_sameAs_only(synset):
    """
    Fonction pour obtenir le fichier "aligned_ontologies_(only_owl_same_as).nt"
    """
    lemon = URIRef(synset["synset"])
    owl = Namespace("http://www.w3.org/2002/07/owl#")
    concept = URIRef("https://sentic.net/api/en/concept/%s" % ("_".join(
        synset["concept"].split(" "))))

    GRAPH.add((lemon, owl.sameAs, concept))


def updateGraph_including_sameAs(synset):
    """
    Fonction pour obtenir le fichier "aligned_ontologies_(includes_owl_same_as).nt"
    """
    lemon = URIRef(synset["synset"])
    owl = Namespace("http://www.w3.org/2002/07/owl#")
    urn = Namespace("urn:absolute:ontosenticnet#")
    concept = URIRef("https://sentic.net/api/en/concept/%s" % ("_".join(
        synset["concept"].split(" "))))

    GRAPH.add((lemon, owl.sameAs, concept))
    GRAPH.add((concept, urn.pleasantness, Literal(
        synset["pleasantness"], datatype=XSD.decimal)))
    GRAPH.add((concept, urn.attention, Literal(
        synset["attention"], datatype=XSD.decimal)))
    GRAPH.add((concept, urn.sensitivity, Literal(
        synset["sensitivity"], datatype=XSD.decimal)))
    GRAPH.add((concept, urn.aptitude, Literal(
        synset["aptitude"], datatype=XSD.decimal)))


def getType(value):
    """
    Convertir les noms en chiffres pour la query
    """
    return 'noun' if value == "1" else (
        'verb' if value == "2" else (
            'adjective' if value == "3" else (
                'adverb' if value == "4" else 'adjective'
            )
        )
    )


if __name__ == "__main__":
    main()
