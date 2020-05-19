"""
ETAPE 2: désambiguisation
"""

from pywsd import disambiguate
from pywsd.similarity import max_similarity as maxsim
from nltk import tokenize
import json

# Variables globales
with open('./restructured_data.json', 'r') as f:
    DATA = json.load(f)
NEW_TEXT_DATA = list()

# Traitement des données
for text_data in DATA.get("donnees_textuelles"):
    # Variables principales de la boucle
    text = text_data.get("texte")
    n = text_data.get("n")
    wsd = list()
    count = 1

    # Séparation en phrases et désambigusation
    sentences = tokenize.sent_tokenize(text)
    for sentence in sentences:
        wsd.extend(disambiguate(sentence, algorithm=maxsim,
                                similarity_option='wup', keepLemmas=True))
        print("Set " + str(n) + ": sentence " +
              str(count) + " out of " + str(len(sentences)))
        count += 1

    # Créer une seconde liste en triant les données
    wsd2 = list()
    for word_data in wsd:
        wsd2.append((word_data[0], word_data[1], word_data[2].name(
        ) if word_data[2] is not None else word_data[2]))

    # Finaliser les nouvelles données
    NEW_TEXT_DATA.append({
        "n": n,
        "texte": text,
        "wsd": wsd2
    })

with open('./hom.od_eng_disamb.json', 'w') as f:
    json.dump({
        "titre": DATA.get("titre"),
        "auteur": DATA.get("auteur"),
        "donnees_textuelles": NEW_TEXT_DATA
    }, f)
