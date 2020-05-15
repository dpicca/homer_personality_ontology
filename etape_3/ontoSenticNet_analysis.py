import json
import time
from nltk.corpus import wordnet as wn
from SPARQLWrapper import SPARQLWrapper

SPARQL = SPARQLWrapper(
    endpoint="http://localhost:3030/OntoSenticNet/sparql", returnFormat="json"
)
GLOBAL_START = time.time()
with open('../etape_2/hom.od_eng_disamb.json', 'r') as input_file:
    DATA = json.load(input_file)


def main():
    texts = DATA.get('donnees_textuelles')
    similarities = getSimilarities(texts)
    output = prepareOutput(similarities)

    with open('./hom.od_eng_OntoSenticNet_analysis_unrestricted.json', 'w') as output_file:
        json.dump({
            "titre": DATA.get("titre"),
            "auteur": DATA.get("auteur"),
            "analyse_ontoSenticNet": output
        }, output_file)
        print("Successfuly created file. Total run time: " +
              str(time.time() - GLOBAL_START))


def getSimilarities(texts):
    similarity_dict = dict()
    for text in texts:
        print("started poem " + text["n"] + "...")
        start_time = time.time()
        similarity_list = list()
        for word in text['wsd']:
            if word[2] is not None:
                word[2] = wn.synset(word[2])
                similarity_list.append(
                    searchOntoSenticNetsSentics(word[2]))
            else:
                word[2] = None
        similarity_dict[text["n"]] = similarity_list
        end_time = time.time()
        print("finished poem " + text["n"] +
              " in " + str(end_time - start_time) +
              " seconds")
    return similarity_dict


def prepareOutput(sims):
    text_data = dict()
    for key, similarities in sims.items():
        print("started data construction for poem " + key + "...")
        start_time = time.time()
        text_data_list = list()
        for similarity in similarities:
            if similarity is not None:
                similarity[2] = " ".join(similarity[2].split("_")) if len(
                    similarity[2].split("_")) > 0 else similarity[2]
                meta_data = queryOntoSenticNetMetadata(similarity[2])
                text_data_list.append({
                    "word": similarity[1].name(),
                    "concept": similarity[2],
                    "sensitivity": meta_data["sens"],
                    "aptitude": meta_data["apt"],
                    "attention": meta_data["att"],
                    "pleasantness": meta_data["plea"],
                })
        text_data[key] = text_data_list
        end_time = time.time()
        print("finished data construction for poem " + key +
              " in " + str(end_time - start_time) +
              " seconds")
    return text_data


def searchOntoSenticNetsSentics(my_word):
    word_data = dict()
    word = my_word.name()
    ontoSenticNetRdyWord = word[:-5]

    word_data["word"] = my_word
    word_data["semantics"] = queryOntoSenticNetSemantics(ontoSenticNetRdyWord)

    if len(word_data.get("semantics")) > 0:
        word = word_data.get("word")
        semantics = word_data.get("semantics")
        itemMaxValue = getBestSimilarity(word, semantics)
        if len(itemMaxValue[1]) > 0:
            return ([max(itemMaxValue[1]), word, itemMaxValue[0]])
        else:
            return
    else:
        # print(my_word.definition())
        return


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
            return None
        # ret is a stream with the results in XML, see <http://www.w3.org/TR/rdf-sparql-XMLres/>
    except:
        print('failed')


def getBestSimilarity(word, semantics):
    semantics_synsets = dict()
    for semantic in semantics:
        semantics_synsets[semantic] = wn.synsets(semantic)
    sims = dict()
    for key in semantics_synsets.keys():
        sims[key] = list()
        for ss in semantics_synsets[key]:
            sims[key].append(wn.wup_similarity(word, ss) or 0)
    return max(sims.items(), key=lambda x: max(
        x[1]) if len(x[1]) > 0 else -1
    )


if __name__ == "__main__":
    main()
