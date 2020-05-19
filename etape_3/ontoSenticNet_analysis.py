"""
ETAPE 3: comparer avec OntoSenticNet
"""

import json
import time
from nltk.corpus import wordnet as wn
from SPARQLWrapper import SPARQLWrapper

# Variables globales
SPARQL = SPARQLWrapper(
    endpoint="http://localhost:3030/OntoSenticNet/sparql", returnFormat="json"
)
GLOBAL_START = time.time()
with open('../etape_2/hom.od_eng_disamb.json', 'r') as input_file:
    DATA = json.load(input_file)


def main():
    """
    Fonction principale :
        - importer les données
        - calculer les similarités
        - préparer l'output
        - créer le fichier d'output
    """
    texts = DATA.get('donnees_textuelles')
    similarities = getSimilarities(texts)
    output = prepareOutput(similarities)

    with open('./hom.od_eng_OntoSenticNet_analysis.json', 'w') as output_file:
        json.dump({
            "titre": DATA.get("titre"),
            "auteur": DATA.get("auteur"),
            "analyse_ontoSenticNet": output
        }, output_file)
        print("Successfuly created file. Total run time: " +
              str(time.time() - GLOBAL_START))


def getSimilarities(texts):
    """
    Fonction d'obtention des similarités
    """
    # Dictionnaire qui contiendra les valeurs finales
    similarity_dict = dict()
    for text in texts:
        print("started poem " + text["n"] + "...")
        start_time = time.time()

        # Liste des similarités pour chaque mots
        similarity_list = list()
        for word in text['wsd']:
            if word[2] is not None:
                word[2] = wn.synset(word[2])
                # Ajouter les similarités récupérées à la liste
                similarity_list.append(
                    searchOntoSenticNetsSentics(word[2]))
            else:
                word[2] = None
        # Ajout des similarités au dictionnaire
        similarity_dict[text["n"]] = similarity_list
        end_time = time.time()
        print("finished poem " + text["n"] +
              " in " + str(end_time - start_time) +
              " seconds")
    return similarity_dict


def prepareOutput(sims):
    """
    Préparer l'output final
    """
    # Variable contenant les données préparées
    text_data = dict()
    for key, similarities in sims.items():
        print("started data construction for poem " + key + "...")
        start_time = time.time()

        # Préparation des données, récupération des infos dans OntoSenticNet
        text_data_list = list()
        for similarity in similarities:
            if (similarity is not None) and (similarity > 0):
                # Si il y a une similarité et qu'elle est suppérieure à 0, on prépare l'output
                similarity[2] = " ".join(similarity[2].split("_")) if len(
                    similarity[2].split("_")) > 0 else similarity[2]
                # Récupération des données dans OntoSenticNet
                meta_data = queryOntoSenticNetMetadata(similarity[2])
                text_data_list.append({
                    "word": similarity[1].name(),
                    "concept": similarity[2],
                    "sensitivity": meta_data["sens"],
                    "aptitude": meta_data["apt"],
                    "attention": meta_data["att"],
                    "pleasantness": meta_data["plea"],
                })
        # Ajouter les données au dictionnaire
        text_data[key] = text_data_list
        end_time = time.time()
        print("finished data construction for poem " + key +
              " in " + str(end_time - start_time) +
              " seconds")
    return text_data


def searchOntoSenticNetsSentics(my_word):
    """
    Fonction de récupération des concept correspondants au synset
    On retourne le concept qui correspond le mieux au synset
    """
    # Dictionnaire contenant les données
    word_data = dict()

    # Récupérer le mot à partir du synset
    word = my_word.name()
    ontoSenticNetRdyWord = word[:-5]

    # Préparation d'un début output
    word_data["word"] = my_word
    # Récupérer les concept dans OntoSenticNet
    word_data["semantics"] = queryOntoSenticNetSemantics(ontoSenticNetRdyWord)

    # Si on a un résultat valide, récupérer les similarités
    if len(word_data.get("semantics")) > 0:
        word = word_data.get("word")
        semantics = word_data.get("semantics")
        # Retourner le concept dont le synset a la plus grande similarité avec le synset en entrée
        itemMaxValue = getBestSimilarity(word, semantics)
        # Si la similarité n'est pas vide, on la retourne
        if len(itemMaxValue[1]) > 0:
            return ([max(itemMaxValue[1]), word, itemMaxValue[0]])
        else:
            return
    else:
        return


def queryOntoSenticNetSemantics(word):
    """
    Interroger OntoSenticNet pour les concepts
    """
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
        # Retourner le concept trouvé sans "urn:absolute:ontosenticnet#"
        return [r.get('semantics').get("value").replace(
            "urn:absolute:ontosenticnet#",
            ""
        ) for r in results]
    except:
        print('failed')


def queryOntoSenticNetMetadata(word):
    """
    Interroger OntoSenticNet pour les données attachées au concept
    """
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
        # Si on a un résultat, on nettoie l'output et retourne
        if len(results) > 0:
            r = results[0]
            del r["word"]
            # Mise en forme de l'output
            for metadata in r.keys():
                val = r[metadata].get("value")
                r[metadata] = val
            return r
        else:
            return None
    except:
        print('failed')


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
