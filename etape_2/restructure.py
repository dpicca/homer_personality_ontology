import json

data = None
with open('../etape_1/hom.od_eng.json', 'r') as f:
    data = json.load(f)

title = data.get('TEI.2', {}).get('teiHeader', {}).get(
    'fileDesc', {}).get('titleStmt', {}).get('title')

author = data.get('TEI.2', {}).get('teiHeader', {}).get(
    'fileDesc', {}).get('titleStmt', {}).get('author')

div = data.get('TEI.2', {}).get('text', {}).get(
    'body', {}).get('div1')

new_text_data = list()
for text_data in div:
    new_text_data.append({
        "n": text_data.get("@n"),
        "texte": text_data.get("p")
    })

with open('./restructured_data.json', 'w') as f:
    json.dump({
        "titre": title,
        "auteur": author,
        "donnees_textuelles": new_text_data
    }, f)
