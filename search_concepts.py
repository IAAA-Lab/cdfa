from rdflib import Graph, URIRef, Literal
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DCTERMS, Namespace

import os

CDFA_BASE_URI = "https://iaaa.es/cdfa/"

FUEROS_FILE = "data/fueros_complete_3_3_26.ttl"
THESAURUS_FILE = "data/tesauro-de-derecho-foral-aragones.rdf"

OUTPUT_FOLDER = "results/"


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

def search_concepts_in_sections(concepts):
    input_model = Graph()
    subjects_model = Graph()
    subjects_model.bind("cdfa", Namespace(CDFA_BASE_URI))
    input_model.parse(FUEROS_FILE,format="turtle")

    log_file = open(OUTPUT_FOLDER+"log.txt", "w")
    for subject, label in concepts:
        search_concept_in_section_titles(subject, label, input_model, subjects_model, log_file)
    log_file.close()
    return subjects_model


def search_concept_in_section_titles(subject, label, input_model, subjects_model, log_file=None):
    query = """
    PREFIX cdfa: <https://iaaa.es/cdfa/>
    PREFIX dct: <http://purl.org/dc/terms/>
    
    SELECT DISTINCT ?section ?title ?page
    WHERE {
        ?section a cdfa:Section .
        ?section dct:title ?title .
        ?section dct:hasPart ?phrase .
        OPTIONAL {?section cdfa:systematicVersionPage ?page} .
        FILTER (lang(?title) = "es") .
        FILTER (CONTAINS(LCASE(?title),?concept)) .
    }
    ORDER BY ?label
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
    PREFIX cdfa: <https://iaaa.es/cdfa/>
    PREFIX dct: <http://purl.org/dc/terms/>
    
    SELECT DISTINCT ?section ?title
    WHERE {
        ?section a cdfa:Section .
        ?section dct:title ?title .
        ?section dct:hasPart ?phrase .
        ?phrase a cdfa:Phrase .
        ?phrase dct:description ?description .
        FILTER (lang(?description) = "es") .
        FILTER (CONTAINS(LCASE(?description),?concept)) .
    }
    ORDER BY ?label
'''


if __name__ == "__main__":

    # configuracion
    # python3 -m venv .venv
    # source .venv/bin/activate
    # VSCode autoactivate environment in Settings, python.terminal.activateEnvironment
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    concepts = return_final_concepts()
    subjects_model = search_concepts_in_sections(concepts)
    subjects_model.serialize(OUTPUT_FOLDER+"output.ttl", format = "turtle")

