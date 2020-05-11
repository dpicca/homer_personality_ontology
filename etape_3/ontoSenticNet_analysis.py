import json
from nltk.corpus import wordnet as wn
from SPARQLWrapper import SPARQLWrapper

SPARQL = SPARQLWrapper(
    endpoint="http://localhost:3030/OntoSenticNet/sparql", returnFormat="json"
)


def main():
    with open('../etape_2/hom.od_eng_disamb.json', 'r') as f:
        data = json.load(f)

    texts = data.get('donnees_textuelles')
    for text in texts:
        for word in text['wsd']:
            if word[2] is not None:
                word[2] = wn.synset(word[2])
                searchOntoSenticNetsSentics(word[2])
            else:
                word[2] = None


def searchOntoSenticNetsSentics(my_word):
    word_data = dict()
    word = my_word.name()
    ontoSenticNetRdyWord = word[:-5]

    word_data["semantics"] = queryOntoSenticNetSemantics(ontoSenticNetRdyWord)
    word_data["metadata"] = queryOntoSenticNetMetadata(ontoSenticNetRdyWord)

    print(word_data)


def queryOntoSenticNetSemantics(word):
    query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX urn: <urn:absolute:ontosenticnet#>

        SELECT *
        WHERE {
            ?word urn:text "%s".
  	        ?word urn:semantics ?semantics
        }
    """ % (word)
    SPARQL.setQuery(query)
    try:
        query_result = SPARQL.query().convert()
        results = query_result.get("results").get("bindings")
        return [r.get('semantics').get("value").replace(
            "urn:absolute:ontosenticnet#",
            ""
        ) for r in results]
    except:
        print('failed')


def queryOntoSenticNetMetadata(word):
    query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX urn: <urn:absolute:ontosenticnet#>

        SELECT *
        WHERE {
            ?word urn:text "%s".
	          ?word urn:sensitivity ?sens.
  	        ?word urn:aptitude ?apt.
  	        ?word urn:attention ?att.
  	        ?word urn:pleasantness ?plea.
        }
    """ % (word)
    SPARQL.setQuery(query)
    try:
        query_result = SPARQL.query().convert()
        results = query_result.get("results").get("bindings")
        if len(results) > 0:
            r = results[0]
            del r["word"]
            for metadata in r.keys():
                val = r[metadata].get("value")
                r[metadata] = val
            return r
        else:
            return results
        # ret is a stream with the results in XML, see <http://www.w3.org/TR/rdf-sparql-XMLres/>
    except:
        print('failed')


if __name__ == "__main__":
    main()
