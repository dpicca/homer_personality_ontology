import json
from SPARQLWrapper import SPARQLWrapper
from nltk.corpus import wordnet as wn
import xml.etree.ElementTree as ET
from xml.dom import minidom
import time

RDF = ET.Element("rdf:RDF", {
    "xmlns:rdf": 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    "xmlns:lemon": 'http://www.lemon-model.net/lemon#',
    "xmlns:ontosenticnet": 'urn:absolute:ontosenticnet#',
})
INPUT_PATH = '../etape_3/hom.od_eng_OntoSenticNet_analysis_unrestricted'
FILE_FORMAT = '.json'
with open(INPUT_PATH + FILE_FORMAT, 'r') as input_file:
    DATA = json.load(input_file)

SPARQL = SPARQLWrapper(
    endpoint='http://localhost:3030/LemonUby/sparql', returnFormat='json'
)


def main():
    texts_words = DATA.get('analyse_ontoSenticNet')
    st = time.time()
    print("starting data conversion...")
    synsets = [{
        "synset": wn.synset(word["word"]).lemmas()[0].key(),
        "concept": word["concept"],
        "sensitivity": word["sensitivity"],
        "aptitude": word["aptitude"],
        "attention": word["attention"],
        "pleasantness": word["pleasantness"],
    } for words in texts_words.values() for word in words]
    print("Converted data in %s seconds" % (time.time() - st))

    count = 1
    total_time = 0
    print("starting data extraction and xml construction...")
    for synset in synsets:
        st = time.time()
        lemon_WN_Sense = queryLemonUby(synset["synset"])
        create_xml(lemon_WN_Sense, synset)
        total_time += time.time() - st
        if count % 403 == 0:
            remaining = total_time/count*(len(synsets)-count)
            print("%s percent done, approx time remaining: %s minutes" %
                  (
                      count / len(synsets)*100,
                      remaining/60
                  )
                  )
        count += 1

    with open("ontology_alignment_unrestricted.rdf", "w") as output_file:
        output_file.write(prettifyXml(RDF))


def queryLemonUby(synset):
    synset_type = synset.split("%")[1][0]
    query = """
        SELECT *
        WHERE {
            ?ref <http://purl.org/olia/ubyCat.owl#externalReference> "[POS: %s] %s".
        }
    """ % (conversion(synset_type), synset)
    SPARQL.setQuery(query)
    try:
        result = SPARQL.query().convert()
        reference = result.get("results").get("bindings")[0].get("ref")
        return reference.get("value").replace(
            "http://lemon-model.net/lexica/uby/wn/",
            ""
        ).replace(
            "#MonolingualExternalRef1",
            ""
        )
    except:
        print("Something went wrong!")


def create_xml(synset, word):
    lexical_sense = ET.SubElement(RDF, "lemon:LexicalSense", {
        "rdf:about": synset
    })
    ET.SubElement(
        lexical_sense,
        "ontosenticnet:concept"
    ).text = word.get("concept")
    ET.SubElement(
        lexical_sense,
        "ontosenticnet:sensitivity"
    ).text = word.get("sensitivity")
    ET.SubElement(
        lexical_sense,
        "ontosenticnet:aptitude"
    ).text = word.get("aptitude")
    ET.SubElement(
        lexical_sense,
        "ontosenticnet:attention"
    ).text = word.get("attention")
    ET.SubElement(
        lexical_sense,
        "ontosenticnet:pleasantness"
    ).text = word.get("pleasantness")


def conversion(value):
    return 'noun' if value == "1" else (
        'verb' if value == "2" else (
            'adjective' if value == "3" else (
                'adverb' if value == "4" else 'adjective'
            )
        )
    )


def prettifyXml(xml):
    rough = ET.tostring(xml, 'utf-8')
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="  ")


if __name__ == "__main__":
    main()
