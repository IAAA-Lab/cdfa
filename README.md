[Website](https://migueldelmolino.es/cdfa/)

Repository with the code to create Linked Data repository and the thesaurus providing the thematic concepts.

Contents of this folder:
- RDFcreation: a folder that contains the Python scripts responsible for generating and populating RDF data.
- data: Turtle and RDF files with the content that should be available in our Linked Data repository
- fuseki : a folder with the configuration of a Fuseki SPARQL end-point container. This Fuseki deployment incorporates textual indexes on the values of dct:title and dct:description properties.
- fuseki_storage_creation.py: In case fueros RDF file isn't uploaded manualy in Fuseki SPARQL end-point, this program creates a new dataset in Fuseki (with the textual indexes) and uploads the RDF data.
- search_concepts.py: Program to generate subject annotations. For each concept (without narrower concepts) in the thesaurus, it look up the preferred label of the concept in the Fueros RDF file. There are two strategies implemented: look for direct matches with CONTAINS function in the section titles, or textual queries of in section titles through the Fuseki end-point container.
- website: a folder that contains all the necessary files to build, run, and deploy the Linked Data portal using a Flask-based service, including configuration, dependencies, and containerization setup.
