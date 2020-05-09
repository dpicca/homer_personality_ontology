import json
from nltk.corpus import wordnet as wn
from SPARQLWrapper import SPARQLWrapper


def main():
    sparql = SPARQLWrapper(
        endpoint="http://localhost:3030/OntoSenticNet/sparql", returnFormat="json"
    )

    with open('../etape_2/hom.od_eng_disamb.json', 'r') as f:
        data = json.load(f)

    texts = data.get('donnees_textuelles')
    for text in texts:
        for word in text['wsd']:
            if word[2] is not None:
                word[2] = wn.synset(word[2])
                searchOntoSenticNetsSentics(word[2], sparql)
            else:
                word[2] = None


def searchOntoSenticNetsSentics(my_word, sparql):
    word = my_word.name()
    ontoSenticNetReadyWord = word[:-5]
    query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX urn: <urn:absolute:ontosenticnet#>

        SELECT ?x ?v
        WHERE {
	          ?x urn:text "%s".
  	        ?x urn:semantics ?v
        }
    """ % (ontoSenticNetReadyWord)

    results = queryOntoSenticNet(query, sparql)
    if len(results) > 0:
        print(ontoSenticNetReadyWord)
        print("-------")
        for r in results:
            print(r["v"]["value"].replace("urn:absolute:ontosenticnet#", ""))
        print("-------")
    else:
        return


def queryOntoSenticNet(query, sparql):
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        return results.get("results").get("bindings")
        # ret is a stream with the results in XML, see <http://www.w3.org/TR/rdf-sparql-XMLres/>
    except:
        print('failed')


if __name__ == "__main__":
    main()
