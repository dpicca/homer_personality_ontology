import json
from SPARQLWrapper import SPARQLWrapper
from nltk.corpus import wordnet as wn
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, XSD


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
    texts_words = DATA.get('analyse_ontoSenticNet')
    synsets = [{
        "synset": wn.synset(word["word"]).lemmas()[0].key(),
        "concept": word["concept"],
        "sensitivity": word["sensitivity"],
        "aptitude": word["aptitude"],
        "attention": word["attention"],
        "pleasantness": word["pleasantness"],
    } for words in texts_words.values() for word in words]

    for synset in synsets:
        synset["synset"] = queryLemonUby(synset["synset"])
        updateGraph(synset)

    GRAPH.serialize(destination="test2" +
                    OUTPUT_FORMAT, format="nt")


def queryLemonUby(synset):
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
        return reference.get("value").split("#")[0]
    except:
        print("Something went wrong!")
        return


def updateGraph(synset):
    lemon = URIRef(synset["synset"])
    owl = Namespace("http://www.w3.org/2002/07/owl#")
    concept = URIRef("https://sentic.net/api/en/concept/%s" % ("_".join(
        synset["concept"].split(" "))))

    GRAPH.add((lemon, owl.sameAs, concept))


def getType(value):
    return 'noun' if value == "1" else (
        'verb' if value == "2" else (
            'adjective' if value == "3" else (
                'adverb' if value == "4" else 'adjective'
            )
        )
    )


if __name__ == "__main__":
    main()
