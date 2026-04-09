# A linked data repository to access historical regional law: the case of the charters of the Aragon Kingdom

# Description

GitHub repository with the code for the generation of a linked data repository from the contents of a [parallel Latin-Spanish corpus with contents of the charters of the Aragon Kingdom](https://zenodo.org/records/18272211).

Contents of this folder:
- RDFcreation: a folder that contains the Python scripts responsible for generating and populating RDF data.
- data: Turtle and RDF files with the content that should be available in our Linked Data repository
- fuseki : a folder with the configuration of a Fuseki SPARQL end-point container. This Fuseki deployment incorporates textual indexes on the values of dct:title and dct:description properties.
- fuseki_storage_creation.py: In case fueros RDF file isn't uploaded manualy in Fuseki SPARQL end-point, this program creates a new dataset in Fuseki (with the textual indexes) and uploads the RDF data.
- search_concepts.py: Program to generate subject annotations. For each concept (without narrower concepts) in the thesaurus, it look up the preferred label of the concept in the Fueros RDF file. There are two strategies implemented: look for direct matches with CONTAINS function in the section titles, or textual queries of in section titles through the Fuseki end-point container.
- website: a folder that contains all the necessary files to build, run, and deploy the Linked Data portal using a Flask-based service, including configuration, dependencies, and containerization setup. A demo of this folder is available at [Website](https://migueldelmolino.es/cdfa/)

# Acknowledgements

This repository is part of the [Miguel del Molino project](https://migueldelmolino.es/) supported by the Aragon Regional Government (Spain) [grant number PROY_S11_24].

## Credits

The work of this Respository is licensed under a [Creative Commons Attribution 4.0 International License][cc-by].

Except where otherwise noted, this content is published under a [CC BY license][cc-by], which means that you can copy, redistribute, remix, transform and build upon the content for any purpose even commercially as long as you give appropriate credit and provide a link to the license.

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg

