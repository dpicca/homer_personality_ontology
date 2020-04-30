"""
ETAPE 1: passer de .XML à .json
"""

import xmltodict
import json
from pprint import pprint

with open("./hom.od_eng.xml", "r") as xml_file:
    xml = xml_file.read()

converted_xml = xmltodict.parse(xml)

with open("hom.od_eng.json", "w") as json_file:
    json.dump(converted_xml, json_file)
