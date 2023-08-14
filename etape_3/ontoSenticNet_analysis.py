"""
ETAPE 3: comparer avec OntoSenticNet
"""

import json
import time
from nltk.corpus import wordnet as wn
from SPARQLWrapper import SPARQLWrapper
from tqdm import tqdm


# Global Variables
SPARQL = SPARQLWrapper(
    endpoint="http://localhost:3030/OntoSenticNet/sparql", returnFormat="json"
)
GLOBAL_START = time.time()
with open('../etape_2/hom.od_eng_disamb_short.json', 'r') as input_file:
    DATA = json.load(input_file)

def main():
    texts = DATA.get('donnees_textuelles')
    similarities = getSimilarities(texts)
    output = prepareOutput(similarities)

    with open('./hom.od_eng_OntoSenticNet_analysis.json', 'w') as output_file:
        json.dump({
            "titre": DATA.get("titre"),
            "auteur": DATA.get("auteur"),
            "analyse_ontoSenticNet": output
        }, output_file)
        print("Successfully created file. Total run time: " +
              str(time.time() - GLOBAL_START))





def getSimilarities(texts):
    similarity_dict = dict()

    # Create a single progress bar
    pbar = tqdm(total=len(texts), desc="Initializing...")

    for text in texts:
        pbar.set_description(f"Processing text {text['n']}")

        similarity_list = list()

        for word in text['wsd']:
            pbar.set_description(f"Processing word {word[0]} in text {text['n']}")

            if word[2] is not None:
                word[2] = wn.synset(word[2])
                similarity_list.append(
                    searchOntoSenticNetsSentics(word[2]))
            else:
                word[2] = None

        similarity_dict[text["n"]] = similarity_list
        pbar.update(1)  # Update the progress bar

    pbar.close()  # Close the progress bar
    return similarity_dict



def prepareOutput(sims):
    text_data = dict()
    for key, similarities in sims.items():
        text_data_list = list()
        for similarity in similarities:
            if (similarity is not None) and any(val > 0 for val in similarity):
                # rest of the code
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
    return text_data

def searchOntoSenticNetsSentics(my_word):
    word_data = dict()
    word = my_word.name()
    ontoSenticNetRdyWord = word[:-5]
    word_data["word"] = my_word
    word_data["semantics"] = queryOntoSenticNetSemantics(ontoSenticNetRdyWord)

    if word_data.get("semantics") and len(word_data.get("semantics")) > 0:
        word = word_data.get("word")
        semantics = word_data.get("semantics")
        itemMaxValue = getBestSimilarity(word, semantics)
        if len(itemMaxValue[1]) > 0:
            return [max(itemMaxValue[1]), word, itemMaxValue[0]]
        else:
            return
    else:
        return




def queryOntoSenticNetSemantics(word):
    """
    Interroger OntoSenticNet pour les concepts
    """
    query = f"""
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX osn: <http://w3id.org/ontosenticnet#>

            SELECT *
            WHERE {{
                ?word osn:semanticTerm ?semantics.
                FILTER (str(?word) = "http://w3id.org/ontosenticnet#{word.lower()}")
            }}
        """

    SPARQL.setQuery(query)
    try:
        query_result = SPARQL.query().convert()
        results = query_result.get("results").get("bindings")

        # Feedback on success

        return [r.get('semantics').get("value").replace(
            "http://w3id.org/ontosenticnet#",
            ""
        ) for r in results]

    except Exception as e:
        print(f"Query failed due to: {e}")



def queryOntoSenticNetMetadata(word):
    """
    Interroger OntoSenticNet pour les données attachées au concept
    """
    print(f"Querying OntoSenticNet for {word}")
    query = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX osn: <http://w3id.org/ontosenticnet#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?property ?value
        WHERE {{
            {{
                <http://w3id.org/ontosenticnet#{word}> ?property ?value.
                FILTER (datatype(?value) = xsd:double)
            }}
            UNION
            {{
                ?value osn:semanticTerm <http://w3id.org/ontosenticnet#{word}>.
                BIND(osn:semanticTerm AS ?property)
            }}
        }}
    """

    SPARQL.setQuery(query)
    try:
        query_result = SPARQL.query().convert()
        results = query_result.get("results", {}).get("bindings", [])

        # If there are results, process and return them
        if results:
            processed_results = {}
            for r in results:
                property_val = r["property"]["value"].split("#")[-1]  # Extracting the last part after '#'
                value_val = r["value"]["value"]
                processed_results[property_val] = value_val
            return processed_results
        else:
            return None
    except Exception as e:
        print(f"Query failed due to: {e}")


def getBestSimilarity(synset, semantics):
    """
    Trouver le concept qui possède le synset le plus similaire au synset d'entrée
    """
    semantics_synsets = dict()
    # Conversion des concepts en synsets avec wordnet
    for semantic in semantics:
        semantics_synsets[semantic] = wn.synsets(semantic)
    sims = dict()
    # Calcul des similarités
    for key in semantics_synsets.keys():
        sims[key] = list()
        # Ajouter la liste des similarités pour chaque synset (des concepts)
        for ss in semantics_synsets[key]:
            sims[key].append(wn.wup_similarity(synset, ss) or 0)
    # Retourner le concept qui possède le synset le plus similaire au synset d'entrée
    return max(sims.items(), key=lambda x: max(
        x[1]) if len(x[1]) > 0 else -1
    )


if __name__ == "__main__":
    main()
