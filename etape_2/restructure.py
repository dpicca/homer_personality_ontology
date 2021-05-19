"""
ETAPE 1.5: Restructurer les données
"""

import json
import re

data = None
with open('../etape_1/hom.od_eng.json', 'r') as f:
    data = json.load(f)

# Récupérer les infos importantes
title = data.get('TEI.2', {}).get('teiHeader', {}).get(
    'fileDesc', {}).get('titleStmt', {}).get('title')

author = data.get('TEI.2', {}).get('teiHeader', {}).get(
    'fileDesc', {}).get('titleStmt', {}).get('author')

div = data.get('TEI.2', {}).get('text', {}).get(
    'body', {}).get('div1')

# Exportation des données restructurées
with open('./restructured_data.json', 'w') as f:
    json.dump({
        "titre": title,
        "auteur": author,
        "donnees_textuelles": [{
            "n": text_data.get("@n"),
            "texte": re.sub(r"–", "-", text_data.get("p"))
        } for text_data in div]
    }, f)
