from sentence_transformers import CrossEncoder

print("Loading reranker...")

reranker = CrossEncoder(
    "BAAI/bge-reranker-base"
)

def rerank(query, retrieved_chunks, top_k=5):

    pairs = []

    for chunk in retrieved_chunks:

        pairs.append(
            (
                query,
                chunk["text"]
            )
        )

    scores = reranker.predict(pairs)

    for chunk, score in zip(
        retrieved_chunks,
        scores
    ):

        chunk["rerank_score"] = float(score)

    reranked = sorted(
        retrieved_chunks,
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return reranked[:top_k]