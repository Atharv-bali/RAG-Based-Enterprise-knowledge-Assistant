import json
import os

PARENT_PATH = "output/parent_chunks.json"

last_loaded_mtime = 0
parent_lookup = {}

def ensure_parent_lookup_loaded():
    global last_loaded_mtime, parent_lookup
    if not os.path.exists(PARENT_PATH):
        return
        
    try:
        mtime = os.path.getmtime(PARENT_PATH)
    except OSError:
        return
        
    if mtime == last_loaded_mtime:
        return
        
    try:
        with open(PARENT_PATH, "r", encoding="utf-8") as f:
            parent_chunks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return
        
    parent_lookup = {parent["parent_id"]: parent["text"] for parent in parent_chunks}
    last_loaded_mtime = mtime

# Attempt pre-load if files exist
try:
    ensure_parent_lookup_loaded()
except Exception as e:
    print(f"Warning: Could not initialize parent lookup database: {e}")

def build_context(
    reranked_chunks
):
    ensure_parent_lookup_loaded()

    context_parts = []

    seen_parents = set()

    for chunk in reranked_chunks:

        parent_id = chunk["parent_id"]

        if parent_id in seen_parents:
            continue

        seen_parents.add(parent_id)

        parent_text = parent_lookup.get(parent_id)

        if parent_text:
            context_parts.append(
                parent_text
            )

    return "\n\n".join(
        context_parts
    )