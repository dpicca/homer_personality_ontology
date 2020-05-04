from pywsd import disambiguate
from pywsd.similarity import max_similarity as maxsim
import json

data = None
with open('./restructured_data.json', 'r') as f:
    data = json.load(f)

text_data = data.get("donnees_textuelles")
new_text_data = list()
for text in text_data:
    text_value = text.get("texte")
    new_text_data.append({
        "n": text.get("n"),
        "texte": text_value,
        "wsd": disambiguate(text_value, algorithm=maxsim, similarity_option='wup', keepLemmas=True)
    })
    print(text.get("n"))

with open('./hom.od_eng_disamb.json', 'w') as f:
    json.dump({
        "titre": data.get("titre"),
        "auteur": data.get("auteur"),
        "donnees_textuelles": new_text_data
    }, f)
