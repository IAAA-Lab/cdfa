from rdflib import Graph, URIRef, Literal
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DCTERMS, Namespace
from SPARQLWrapper import SPARQLWrapper, JSON

import os

CDFA_BASE_URI = "https://iaaa.es/cdfa/"

FUEROS_FILE = "data/fueros_complete.ttl"
THESAURUS_FILE = "data/tesauro-de-derecho-foral-aragones.rdf"

OUTPUT_FOLDER = "results/"

LOG_CONTAINS = "log_contains.txt"
SUBJECT_ANNOTATIONS_CONTAINS = "subject_annotations_contains.ttl"

LOG_TEXT_INDEX = "log_text_index.txt"
SUBJECT_ANNOTATIONS_TEXT_INDEX = "subject_annotations_text_index.ttl"

FUSEKI_HOST = 'http://localhost:3030'
DATASET_NAME = 'datasetFueros'
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin'
ENDPOINT = f'{FUSEKI_HOST}/{DATASET_NAME}/sparql'



def return_final_concepts():
    model = Graph()
    model.parse(THESAURUS_FILE)
    query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    
    SELECT DISTINCT ?subject ?label
    WHERE {
        ?subject a skos:Concept .
        ?subject skos:prefLabel ?label .
        FILTER NOT EXISTS { ?subject skos:narrower ?anotherConcept } .
    }
    ORDER BY ?label
    """
    results = model.query(query)
    concepts = []
    for row in results:
        concepts.append((row.subject, row.label.lower()))
        # print(f"{row.label}")
    return concepts #1092 concepts

def search_concepts_in_sections_contains(concepts):
    input_model = Graph()
    subjects_model = Graph()
    subjects_model.bind("cdfa", Namespace(CDFA_BASE_URI))
    input_model.parse(FUEROS_FILE,format="turtle")

    log_file = open(OUTPUT_FOLDER+ LOG_CONTAINS, "w")
    for subject, label in concepts:
        search_concept_in_section_titles_contains(subject, label, input_model, subjects_model, log_file)
    log_file.close()
    return subjects_model


def search_concept_in_section_titles_contains(subject, label, input_model, subjects_model, log_file=None):
    query = """
    PREFIX cdfa: <https://iaaa.es/cdfa/>
    PREFIX dct: <http://purl.org/dc/terms/>
    
    SELECT DISTINCT ?section ?title ?page
    WHERE {
        ?section a cdfa:Section .
        ?section dct:title ?title .
        OPTIONAL {?section cdfa:systematicVersionPage ?page} .
        FILTER ((lang(?title) = "es") && CONTAINS(LCASE(?title),?concept)) .
    }
    ORDER BY ?title
    """
    results = input_model.query(query, initBindings={"concept": Literal(label)})

    if log_file is not None:
        log_file.write(f"{label}:\n")
    for row in results:
        if log_file is not None:
            log_file.write(f"\t{row.title} {row.page}: {row.section} dct:subject {subject}\n")
        section_uri = URIRef(row.section)
        subject_uri = URIRef(subject)
        subjects_model.add((section_uri,DCTERMS.subject,subject_uri) )

'''
    # An example of query looking up the concept inside the phrases
    PREFIX cdfa: <https://iaaa.es/cdfa/>
    PREFIX dct: <http://purl.org/dc/terms/>
    
    SELECT DISTINCT ?section ?title
    WHERE {
        ?section a cdfa:Section .
        ?section dct:title ?title .
        ?section dct:hasPart ?phrase .
        ?phrase a cdfa:Phrase .
        ?phrase dct:description ?description .
        FILTER ((lang(?description) = "es") && CONTAINS(LCASE(?description),?concept)) .
    }
    ORDER BY ?description
'''

def search_concepts_in_sections_text_index(concepts):
    sparql = SPARQLWrapper(ENDPOINT)
    input_model = Graph()
    subjects_model = Graph()
    subjects_model.bind("cdfa", Namespace(CDFA_BASE_URI))
    input_model.parse(FUEROS_FILE,format="turtle")

    log_file = open(OUTPUT_FOLDER+LOG_TEXT_INDEX, "w")
    for subject, label in concepts:
        search_concept_in_section_titles_text_index(subject, label, sparql, subjects_model, log_file)
    log_file.close()
    return subjects_model



def search_concept_in_section_titles_text_index(subject, label, sparql, subjects_model, log_file):
    query = """
    PREFIX cdfa: <https://iaaa.es/cdfa/>
    PREFIX text: <http://jena.apache.org/text#>
    PREFIX dct: <http://purl.org/dc/terms/>
    SELECT DISTINCT ?section ?score ?title ?page WHERE {
        ?section a cdfa:Section .
        ?section dct:title ?title .
        OPTIONAL {?section cdfa:systematicVersionPage ?page} .
        (?section ?score) text:query (dct:title '""" + label + """') .
        FILTER (lang(?title)="es" && ?score > 2.0) .
    } ORDER BY DESC(?score)
    """
    results = sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    # printResults(results)
    if log_file is not None:
        log_file.write(f"{label}:\n")
    for row in results["results"]["bindings"]:
        if log_file is not None:
            log_file.write(f"\t{row['title']['value']} {row['page']['value']} {row['score']['value']}: {row['section']['value']} dct:subject {subject}\n")
        section_uri = URIRef(row['section']['value'])
        subject_uri = URIRef(subject)
        subjects_model.add((section_uri,DCTERMS.subject,subject_uri) )

'''
    # An example of query combining two text queries
    PREFIX cdfa: <https://iaaa.es/cdfa/>
    PREFIX text: <http://jena.apache.org/text#>
    PREFIX dct: <http://purl.org/dc/terms/>
    SELECT DISTINCT ?section ?scoretot WHERE {
        ?section a cdfa:Section .
        ?section dct:title ?title .
        ?section dct:hasPart ?phrase .
        ?phrase a cdfa:Phrase .
  		?phrase dct:description ?description .
        OPTIONAL { (?section ?score1) text:query (dct:title 'causas de judios') }
  		  OPTIONAL { (?phrase ?score2) text:query (dct:description 'causas de judios') }
        BIND (COALESCE(?score1,0) + COALESCE(?score2,0) AS ?scoretot)
        FILTER ((?scoretot >0) && (lang(?title)="es") && (lang(?description)="es"))
      } ORDER BY DESC(?scoretot)
'''

if __name__ == "__main__":

    # configuracion
    # python3 -m venv .venv
    # source .venv/bin/activate
    # VSCode autoactivate environment in Settings, python.terminal.activateEnvironment
    # pip freeze > requirements.txt
    # pip install -r requirements.txt
    # apt-get install python3-tk
    # python3 -m pip install SPARQLWrapper
    

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    concepts = return_final_concepts()
    subjects_model = search_concepts_in_sections_contains(concepts)
    subjects_model.serialize(OUTPUT_FOLDER+ SUBJECT_ANNOTATIONS_CONTAINS, format = "turtle")

    subjects_model = search_concepts_in_sections_text_index(concepts)
    subjects_model.serialize(OUTPUT_FOLDER+ SUBJECT_ANNOTATIONS_TEXT_INDEX, format = "turtle")