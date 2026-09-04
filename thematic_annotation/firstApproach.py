import json
import ollama
import numpy as np

# Configuration
MODEL_NAME = "qwen3:14b" #gemma4:e4b"
EMBED_MODEL = "nomic-embed-text"
CLASSES_FILE = "thesaurus.json"
DATA_FILE = "512.txt"  # SlectedConcept.txt"

# Maximum number of characters to send to the models
MAX_CHARS = 5000

# 1. Load and Pre-index Classes
with open(CLASSES_FILE, 'r', encoding='utf-8') as f:
    thesaurus = json.load(f)['thesaurus']

# Combine class name and indicators for better semantic matching
class_texts = [f"{item['class']}: {', '.join(item['indicators'])}" for item in thesaurus]

# Generate embeddings for all classes
print("Generating embeddings for classes... please wait.")
class_embeddings = [
    ollama.embeddings(model=EMBED_MODEL, prompt=text)['embedding']
    for text in class_texts
]
class_embeddings = np.array(class_embeddings)

# 2. Generator to read file section by section
def read_sections(filename):
    """Reads file line by line without loading the whole file into RAM."""
    with open(filename, 'r', encoding='utf-8') as f:
        section_data = ""
        section_id = None

        for line in f:
            if line.strip().startswith("Section"):
                if section_id:
                    yield section_id, section_data
                section_id = line.strip()
                section_data = ""
            else:
                section_data += line

        if section_id:
            yield section_id, section_data

# 3. Embedding search function
def get_top_k_classes(paragraph, k=20):
    # Truncate long paragraphs to avoid context-length errors
    paragraph = paragraph[:MAX_CHARS]

    para_embed = np.array(
        ollama.embeddings(
            model=EMBED_MODEL,
            prompt=paragraph
        )['embedding']
    )

    # Cosine similarity
    similarities = np.dot(class_embeddings, para_embed) / (
        np.linalg.norm(class_embeddings, axis=1) *
        np.linalg.norm(para_embed)
    )

    top_indices = np.argsort(similarities)[-k:][::-1]
    return [thesaurus[i]['class'] for i in top_indices]

# 4. Main Processing Loop
print("Starting classification...")

for section_id, paragraph in read_sections(DATA_FILE):
    if not paragraph.strip():
        continue

    # Truncate before sending to Gemma as well
    paragraph = paragraph[:MAX_CHARS]

    relevant_classes = get_top_k_classes(paragraph, k=20)

    prompt = f"""
Act as a legal classifier. The following text may belong to MULTIPLE categories.

Available categories to choose from: {', '.join(relevant_classes)}.

Paragraph:
{paragraph.strip()}

Task: Identify all categories from the list above that apply to the text.
Return the result as a comma-separated list of names. If none apply, return 'Otro'.
"""

    res = ollama.chat(
        model=MODEL_NAME,
        think=True,
        messages=[{'role': 'user', 'content': prompt}]
    )

    print(f"{section_id}: {res['message']['content'].strip()}")
