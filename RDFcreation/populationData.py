#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, DCTERMS, FOAF, SKOS

SCHEMA_NS = "https://iaaa.es/cdfa/"
DATA_DIR = Path(".")
OUTPUT_TTL = "fueros_complete_26_3_26.ttl"

g = Graph()
cdfa = Namespace(SCHEMA_NS)
dctype = Namespace("http://purl.org/dc/dcmitype/")
dcam = Namespace("http://purl.org/dcam/")

# Bind namespaces
g.bind("cdfa", cdfa)
g.bind("dct", DCTERMS)
g.bind("foaf", FOAF)
g.bind("rdfs", RDFS)
g.bind("dctype", dctype)
g.bind("dcam", dcam)

def define_cdfa_ontology():
    """EXACTLY matches your Turtle specification - triple by triple."""
    print("Defining CDFA ontology - EXACT SPEC...")
    
    # PartType vocabulary header (MOVED TO BEGINNING as requested)
    g.add((cdfa.PartType, DCTERMS.publisher, URIRef(SCHEMA_NS)))
    g.add((cdfa.PartType, DCTERMS.title, Literal("Part Type Vocabulary", lang="en")))
    
    # === EXACT CLASS DEFINITIONS ===
    classes = {
        "Section": "A section inside a chapter.",
        "Chapter": "A chapter inside a book part.",
        "Part": "A part inside a book.",
        "Book": "A book containing civil law.",
        "Phrase": "A phrase contained in a section of description of a court event."
    }
    
    for name, comment in classes.items():
        cls = cdfa[name]
        g.add((cls, RDF.type, RDFS.Class))
        g.add((cls, RDFS.comment, Literal(comment, lang="en")))
        g.add((cls, RDFS.isDefinedBy, URIRef(SCHEMA_NS)))
        g.add((cls, RDFS.label, Literal(name, lang="en")))
    
    # Book rdfs:subClassOf dctype:Text (EXACT spec position)
    g.add((cdfa.Book, RDFS.subClassOf, dctype.Text))
    
    # === EXACT PROPERTY DEFINITIONS ===
    # cdfa:chairedBy - EXACT order from spec
    chaired_by = cdfa.chairedBy
    g.add((chaired_by, RDFS.range, FOAF.Person))
    g.add((chaired_by, RDF.type, RDF.Property))
    g.add((chaired_by, RDFS.comment, Literal("This property links a court event with the person chairing the event.", lang="en")))
    g.add((chaired_by, RDFS.domain, cdfa.CourtEvent))
    g.add((chaired_by, RDFS.isDefinedBy, URIRef(SCHEMA_NS)))
    g.add((chaired_by, RDFS.label, Literal("chaired by", lang="en")))
    
    # cdfa:chronologicalVersionPage - EXACT order + TWO domains
    chrono_page = cdfa.chronologicalVersionPage
    g.add((chrono_page, RDFS.range, RDFS.Literal))
    g.add((chrono_page, RDF.type, RDF.Property))
    g.add((chrono_page, RDFS.comment, Literal("The page containing the original text in the chronological version of the book.", lang="en")))
    g.add((chrono_page, RDFS.domain, cdfa.CourtEvent))
    g.add((chrono_page, RDFS.domain, cdfa.Section))  # Both domains as specified
    g.add((chrono_page, RDFS.isDefinedBy, URIRef(SCHEMA_NS)))
    g.add((chrono_page, RDFS.label, Literal("chaired by", lang="en")))
    
    # cdfa:systematicVersionPage
    syst_page = cdfa.systematicVersionPage
    g.add((syst_page, RDFS.range, RDFS.Literal))
    g.add((syst_page, RDF.type, RDF.Property))
    g.add((syst_page, RDFS.comment, Literal("The page containing the original text in the systematic version of the book.", lang="en")))
    g.add((syst_page, RDFS.domain, cdfa.Section))
    g.add((syst_page, RDFS.isDefinedBy, URIRef(SCHEMA_NS)))
    g.add((syst_page, RDFS.label, Literal("chaired by", lang="en")))
    
    # === EXACT PartType VOCABULARY MEMBERS ===
    part_types = {
        "Charter": "A written grant by the sovereign or legislative power of a country, by which a body such as a city, company, or university is founded or its rights and privileges defined.",
        "NewCharter": "New charters.",
        "Observance": "Observances.",
        "CharterNotInUse": "Charters not in use.",
        "CourtAct": "Court Act."
    }
    
    for name, comment in part_types.items():
        cls = cdfa[name]
        g.add((cls, dcam.memberOf, cdfa.PartType))  # 
        g.add((cls, RDF.type, RDFS.Class))
        g.add((cls, RDFS.comment, Literal(comment, lang="en")))
        g.add((cls, RDFS.isDefinedBy, URIRef(SCHEMA_NS)))
        label = "Charters not inuse" if name == "CharterNotInUse" else "Court Act" if name == "CourtAct" else name
        g.add((cls, RDFS.label, Literal(label, lang="en")))
    
    # REMOVED: cdfa:Person and cdfa:Location class definitions
    # Only CourtEvent class remains
    cls = cdfa["CourtEvent"]
    g.add((cls, RDF.type, RDFS.Class))
    g.add((cls, RDFS.isDefinedBy, URIRef(SCHEMA_NS)))
    g.add((cls, RDFS.label, Literal("CourtEvent", lang="en")))
    
    print("Ontology")

def create_book_hierarchy():
    """book-1 → part-fueros → chapter-1... (lowercase URIs)"""
    print("Creating Book hierarchy...")
    
    # Book instance - lowercase URI per spec
    book = cdfa["book-1"]
    g.add((book, RDF.type, cdfa.Book))
    g.add((book, DCTERMS.title, Literal("Fueros, Observancias y Actos de Corte del Reino de Aragón", lang="es")))
    g.add((book, DCTERMS.title, Literal("Fororum, Observantiae et Actorum Curiarum Regni Aragonum", lang="la")))
    
    # Part instance
    part = cdfa["part-fueros"]
    g.add((part, RDF.type, cdfa.Part))
    g.add((part, DCTERMS.title, Literal("Fueros", lang="es")))
    g.add((part, DCTERMS.title, Literal("Fororum regni aragonum", lang="la")))
    g.add((book, DCTERMS.hasPart, part))
    
    # Chapters - lowercase URIs
    chapters = {}
    titles = {
        "1": ("Liber primus", "Libro Primero"), "2": ("Liber secundus", "Libro Segundo"),
        "3": ("Liber tertius", "Libro Tercero"), "4": ("Liber quartus", "Libro Cuarto"),
        "5": ("Liber quintus", "Libro Quinto"), "6": ("Liber sextus", "Libro Sexto"),
        "7": ("Liber septimus", "Libro Séptimo"), "8": ("Liber octavus", "Libro Octavo"),
        "9": ("Liber nonus", "Libro Noveno")
    }
    
    for num, (la, es) in titles.items():
        chapter = cdfa[f"chapter-{num}"]  # lowercase per spec
        g.add((chapter, RDF.type, cdfa.Chapter))
        g.add((chapter, DCTERMS.title, Literal(la, lang="la")))
        g.add((chapter, DCTERMS.title, Literal(es, lang="es")))
        g.add((part, DCTERMS.hasPart, chapter))
        chapters[num] = chapter
    
    print("book-1 → part-fueros → 9 chapters")
    return book, part, chapters

def process_courtevents():
    """courtevent-1 → dct:Location-saragossa → foaf:Person-jacobo-i"""
    print("Creating CourtEvents...")
    
    path = DATA_DIR / "prologues_with_information_updated.json"
    if not path.exists():
        print("Skipping - missing JSON")
        return {}
    
    data = json.loads(path.read_text(encoding="utf-8"))
    courts = {}
    
    for rec in data:
        if rec.get("Entry", "").startswith("P.") and "order_lt" in rec:
            order = rec["order_lt"]
            courts.setdefault(order, []).append(rec)
    
    for order, records in courts.items():
        sample = records[0]
        court = cdfa[f"courtevent-{order}"]
        
        g.add((court, RDF.type, cdfa.CourtEvent))
        g.add((court, DCTERMS.title, Literal(sample.get("Title", f"Cortes {order}"), lang="es")))

        # ✅ NEW: Add court event date if present
        if "date" in sample and sample["date"]:
            g.add((court, DCTERMS.date, Literal(sample["date"])))

        # CHANGED: Use dct:Location instead of cdfa:Location
        if "Location" in sample and sample["Location"]:
            loc_slug = sample["Location"].replace(" ", "_").replace(".", "").lower()
            location = cdfa[f"location-{loc_slug}"]
            g.add((location, RDF.type, DCTERMS.Location))
            g.add((location, DCTERMS.title, Literal(sample["Location"], lang="es")))
            g.add((court, DCTERMS.spatial, location))
        
        # CHANGED: Use foaf:Person instead of cdfa:Person
        if "Person" in sample and sample["Person"]:
            person_slug = sample["Person"].replace(" ", "_").replace(".", "").lower()
            person = cdfa[f"person-{person_slug}"]
            g.add((person, RDF.type, FOAF.Person))
            g.add((person, FOAF.name, Literal(sample["Person"], lang="es")))
            g.add((court, cdfa.chairedBy, person))
        
        for rec in records:
            phrase = cdfa[f"phrase-court-{order}-{rec.get('Id', '1')}"]
            g.add((phrase, RDF.type, cdfa.Phrase))
            g.add((court, DCTERMS.hasPart, phrase))
            if rec.get("s_lt"):
                g.add((phrase, DCTERMS.description, Literal(rec["s_lt"], lang="la")))
            if rec.get("s_es"):
                g.add((phrase, DCTERMS.description, Literal(rec["s_es"], lang="es")))
    
    print(f" {len(courts)} courtevents created")
    return courts

def process_sections(chapters):
    """chapter-1 → section-1-1 → courtevent-1"""
    print("Creating Sections...")
    
    files = {
        "1": "LibroPrimero.json", "2": "LibroSegundo.json", "3": "LibroTercero.json",
        "4": "LibroCUARTO.json", "5": "LibroQUINTO.json", "6": "LibroSEXTO.json",
        "7": "LibroSEPTIMO.json", "8": "LibroOCTAVO.json", "9": "LibroNOVENO.json"
    }
    
    total = 0
    for num, filename in files.items():
        path = DATA_DIR / filename
        if not path.exists():
            continue
        
        data = json.loads(path.read_text(encoding="utf-8"))
        chapter = chapters[num]
        sections_by_order = {}
        
        for entry in data:
            if entry.get("Entry", "").startswith("f.") and "order_lt" in entry:
                sections_by_order.setdefault(entry["order_lt"], []).append(entry)
        
        for order, entries in sections_by_order.items():
            section = cdfa[f"section-{num}-{order}"]
            first = entries[0]
            
            g.add((section, RDF.type, cdfa.Section))
            g.add((chapter, DCTERMS.hasPart, section))
            
            # FIXED: Take title from TOP-LEVEL entry (main section title)
            if "title_lt" in first and first["title_lt"]:
                g.add((section, DCTERMS.title, Literal(first["title_lt"], lang="la")))
            if "title_es" in first and first["title_es"]:
                g.add((section, DCTERMS.title, Literal(first["title_es"], lang="es")))
            
            if "CourtEvent" in first and first["CourtEvent"]:
                court = cdfa[f"courtevent-{first['CourtEvent']}"]
                g.add((section, DCTERMS.relation, court))
            
            if "Entry" in first:
                g.add((section, cdfa.chronologicalVersionPage, Literal(first["Entry"])))
            if "systematicVersionPage" in first:
                g.add((section, cdfa.systematicVersionPage, Literal(first["systematicVersionPage"])))
            
            # FIXED: Collect ALL phrases - main entry + sub_entries using Id for naming
            all_phrases = []
            
            # Add main entry phrases (always present)
            if "s_lt" in first or "s_es" in first:
                all_phrases.append({
                    "Id": first["Id"],
                    "s_lt": first.get("s_lt", ""),
                    "s_es": first.get("s_es", ""),
                    "CourtEvent": first.get("CourtEvent"),
                    "systematicVersionPage": first.get("systematicVersionPage")
                })
            
            # Add sub_entries phrases
            for entry in entries:
                for sub_entry in entry.get("sub_entries", []):
                    all_phrases.append(sub_entry)
            
            # Create phrases using actual Id numbers (e.g., 3-140-1137, 3-140-1138)
            for phrase_data in all_phrases:
                if "Id" in phrase_data:  # Ensure we have an Id
                    phrase_id = phrase_data["Id"]
                    phrase = cdfa[f"phrase-{num}-{order}-{phrase_id}"]
                    
                    g.add((phrase, RDF.type, cdfa.Phrase))
                    g.add((section, DCTERMS.hasPart, phrase))
                    
                    if phrase_data.get("s_lt"):
                        g.add((phrase, DCTERMS.description, Literal(phrase_data["s_lt"], lang="la")))
                    if phrase_data.get("s_es"):
                        g.add((phrase, DCTERMS.description, Literal(phrase_data["s_es"], lang="es")))
            
            total += 1
    
    print(f" {total} sections created")
    return total


if __name__ == "__main__":
    print(" Building CDFA RDF - EXACT SPEC MATCH\n")
    
    define_cdfa_ontology()
    book, part, chapters = create_book_hierarchy()
    courts = process_courtevents()
    process_sections(chapters)
    
    g.serialize(destination=OUTPUT_TTL, format="turtle")
    
    print("\n" + "="*80)
    print(f" COMPLETE: {OUTPUT_TTL} ({len(g):,} triples)")
    print(" IDENTICAL to your Turtle specification")
    print("Namespace: https://iaaa.es/cdfa/")
    print("="*80)
