import os 
import json
from pathlib import Path

PARENT_CHUNK_SIZE = 2048
CHILD_CHUNK_SIZE = 512

INPUT_DIR = "data/parsed_docs"
OUTPUT_DIR = "output"

# For OS related tasks like creating folder
os.makedirs(OUTPUT_DIR, exist_ok=True)
# For splitting text into tokens, for ex: "Hello world" -> ["Hello", "world"] 
def split_into_tokens(text):
    return text.split()

# For joining tokens back into text, for ex: ["Hello", "world"] -> "Hello world"
def join_tokens(tokens):
    return ' '.join(tokens)

def create_parent_chunks(text):
    # Split the text into tokens and create parent chunks of size PARENT_CHUNK_SIZE
    tokens = split_into_tokens(text)
    parent = []
    for i in range(0,len(tokens), PARENT_CHUNK_SIZE):
        chunk_tokens = tokens[i:i+PARENT_CHUNK_SIZE]

        parent.append({
            "parent_id": f"p{len(parent)+1}",
            "text": join_tokens(chunk_tokens)
        })
    return parent

def create_child_chunks(parent_chunks):

    child_chunks = []
    parent_map = {}

    child_counter = 1

    # This gives us smaller chunks of text from parent chunk, known as child chunk
    for parent in parent_chunks:
        # Taking the parent chunks and then diving into smaller chunks
        parent_id = parent["parent_id"]

        tokens = split_into_tokens(parent["text"])

        for i in range(0, len(tokens), CHILD_CHUNK_SIZE):

            child_tokens = tokens[i:i + CHILD_CHUNK_SIZE]

            child_id = f"c{child_counter}"

            child_chunks.append(
                {
                    "child_id": child_id,
                    "parent_id": parent_id,
                    "text": join_tokens(child_tokens)
                }
            )

            parent_map[child_id] = parent_id

            child_counter += 1

    return child_chunks, parent_map

def load_markdown_documents():

    all_text = []

    # Finds all .md files
    for file in Path(INPUT_DIR).glob("*.md"):

        print(f"Processing: {file}")

        with open(file, "r", encoding="utf-8") as f:
            all_text.append(f.read())

    return "\n\n".join(all_text)

#Save python objects as json file, for ex: {"key": "value"} -> key_value.json
def save_json(data, path):

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():

    # Loads all the markdown documents text into a single string
    text = load_markdown_documents()

    print("Creating parent chunks...")
    
    parent_chunks = create_parent_chunks(text)

    print("Creating child chunks...")

    child_chunks, parent_map = create_child_chunks(parent_chunks)

    save_json(
        parent_chunks,
        os.path.join(OUTPUT_DIR, "parent_chunks.json")
    )

    save_json(
        child_chunks,
        os.path.join(OUTPUT_DIR, "child_chunks.json")
    )

    save_json(
        parent_map,
        os.path.join(OUTPUT_DIR, "parent_map.json")
    )

    print(f"Parents: {len(parent_chunks)}")
    print(f"Children: {len(child_chunks)}")

    print("Done!")


if __name__ == "__main__":
    main()