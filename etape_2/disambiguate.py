from pywsd import disambiguate
from pywsd.similarity import max_similarity as maxsim
from nltk import tokenize
import json

with open('./restructured_data.json', 'r') as f:
    data = json.load(f)

new_text_data = list()

for text_data in data.get("donnees_textuelles"):
    text = text_data.get("texte")
    n = text_data.get("n")
    wsd = list()

    count = 1
    sentences = tokenize.sent_tokenize(text)
    for sentence in sentences:
        wsd.extend(disambiguate(sentence, keepLemmas=True))
        print("Set " + str(n) + ": sentence " +
              str(count) + " out of " + str(len(sentences)))
        count += 1

    wsd2 = list()
    for word_data in wsd:
        wsd2.append((word_data[0], word_data[1], word_data[2].name(
        ) if word_data[2] is not None else word_data[2]))

    new_text_data.append({
        "n": n,
        "texte": text,
        "wsd": wsd2
    })

with open('./hom.od_eng_disamb_2.json', 'w') as f:
    json.dump({
        "titre": data.get("titre"),
        "auteur": data.get("auteur"),
        "donnees_textuelles": new_text_data
    }, f)
