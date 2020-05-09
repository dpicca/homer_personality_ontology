import json
from nltk.corpus import wordnet as wn
from SPARQLWrapper import SPARQLWrapper

sparql = SPARQLWrapper(
    endpoint="http://localhost:3030/OntoSenticNet/sparql", returnFormat="json"
)
my_word = "negative"
query = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX urn: <urn:absolute:ontosenticnet#>

    SELECT ?x ?v
    WHERE {
	      ?x urn:text "%s".
  	    ?x urn:semantics ?v
    }
""" % (my_word)


sparql.setQuery(query)

try:
    results = sparql.query().convert()
    print(results)
    # ret is a stream with the results in XML, see <http://www.w3.org/TR/rdf-sparql-XMLres/>
except:
    print('failed')

with open('../etape_2/hom.od_eng_disamb.json', 'r') as f:
    data = json.load(f)

texts = data.get('donnees_textuelles')
for text in texts:
    for word in text['wsd']:
        word[2] = wn.synset(word[2]) if word[2] is not None else None
