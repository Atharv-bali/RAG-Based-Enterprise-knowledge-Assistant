import json
import os
from rank_bm25 import BM25Okapi

CHUNK_PATH = "output/child_chunks.json"

last_loaded_mtime = 0
child_chunks = []
bm25 = None

def ensure_bm25_loaded():
    global last_loaded_mtime, child_chunks, bm25
    if not os.path.exists(CHUNK_PATH):
        return
        
    try:
        mtime = os.path.getmtime(CHUNK_PATH)
    except OSError:
        return
        
    if mtime == last_loaded_mtime and bm25 is not None:
        return
        
    try:
        with open(CHUNK_PATH, "r", encoding="utf-8") as f:
            new_chunks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return
        
    if new_chunks:
        child_chunks = new_chunks
        tokenized_corpus = [
            chunk["text"].lower().split()
            for chunk in child_chunks
        ]
        bm25 = BM25Okapi(tokenized_corpus)
        last_loaded_mtime = mtime

# Attempt pre-load if files exist
try:
    ensure_bm25_loaded()
except Exception as e:
    print(f"Warning: Could not initialize BM25 database: {e}")

def bm25_search(query, top_k=20):
    ensure_bm25_loaded()
    if not bm25 or not child_chunks:
        return []

    query_tokens = query.lower().split()

    scores = bm25.get_scores(query_tokens)

    ranked_results = sorted(
        # enumerate indexes the scores
        enumerate(scores),
        # Sorts the scores in descending order
        key=lambda x: x[1],
        reverse=True
    )[:top_k]

    results = []

    for rank, (idx, score) in enumerate(
        ranked_results,
        start=1
    ):

        chunk = child_chunks[idx]

        results.append(
            {
                "child_id": chunk["child_id"],
                "parent_id": chunk["parent_id"],
                "text": chunk["text"],
                "rank": rank,
                "score": float(score)
            }
        )

    return results