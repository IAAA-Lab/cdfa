import json
import ollama

MODEL_NAME = "qwen3:14b" #gemma4:e4b"
CLASSES_FILE = "thesaurus.json"
DATA_FILE = "512.txt" #SlectedConcept.txt"

CHUNK_SIZE = 50

# Load classes
with open(CLASSES_FILE, "r", encoding="utf-8") as f:
    thesaurus = json.load(f)["thesaurus"]

all_classes = [item["class"] for item in thesaurus]


def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def read_sections(filename):
    with open(filename, "r", encoding="utf-8") as f:
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


print("Starting classification...")

for section_id, paragraph in read_sections(DATA_FILE):

    if not paragraph.strip():
        continue

    final_classes = set()

    for group in chunk_list(all_classes, CHUNK_SIZE):

        prompt = f"""
You are a legal classifier.

Paragraph:
{paragraph}

Available categories:
{', '.join(group)}

Task:
Select ALL categories that apply.

Rules:
- Choose only from the available categories.
- If none apply, return ONLY "NONE".
- Return only a comma-separated list.
"""

        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result = response["message"]["content"].strip()

        if result.upper() != "NONE":

            for c in result.split(","):
                final_classes.add(c.strip())

    if final_classes:
        print(f"{section_id}: {', '.join(sorted(final_classes))}")
    else:
        print(f"{section_id}: Otro")
