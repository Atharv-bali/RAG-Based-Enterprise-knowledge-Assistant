import json
from rank_bm25 import BM25Okapi

CHUNK_PATH = "output/child_chunks.json"

with open(CHUNK_PATH, "r", encoding="utf-8") as f:
    child_chunks = json.load(f)

tokenized_corpus = [
    chunk["text"].lower().split()
    for chunk in child_chunks
]

bm25 = BM25Okapi(tokenized_corpus)


def bm25_search(query, top_k=20):

    query_tokens = query.lower().split()

    scores = bm25.get_scores(query_tokens)

    ranked_results = sorted(
        enumerate(scores),
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