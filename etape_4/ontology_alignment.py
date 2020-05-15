import json
from SPARQLWrapper import SPARQLWrapper
from nltk.corpus import wordnet as wn

INPUT_PATH = '../etape_3/hom.od_eng_OntoSenticNet_analysis_unrestricted'
FILE_FORMAT = '.json'
with open(INPUT_PATH + FILE_FORMAT, 'r') as input_file:
    DATA = json.load(input_file)

SPARQL = SPARQLWrapper(
    endpoint='http://localhost:3030/LemonUby/sparql', returnFormat='json'
)


def main():
    texts_words = DATA.get('analyse_ontoSenticNet')
    for _, words in texts_words.items():
        for word in words:
            print(queryLemonUby(word.get('word')))


def queryLemonUby(synset):
    sense_key = wn.synset(synset).lemmas()[0].key()
    query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX urn: <urn:absolute:ontosenticnet#>

        SELECT *
        WHERE {
            ?ref <http://purl.org/olia/ubyCat.owl#externalReference> ?synset .
            FILTER( contains(lcase(?synset), '%s' ))
        }
    """ % sense_key
    SPARQL.setQuery(query)
    try:
        reference = SPARQL.query().convert().get(
            "results").get("bindings")[0].get("ref")
        return reference.get("value").replace(
            "http://lemon-model.net/lexica/uby/wn/",
            ""
        ).replace(
            "#MonolingualExternalRef1",
            ""
        )
    except:
        print("lol")


if __name__ == "__main__":
    main()
