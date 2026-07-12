from collections import defaultdict

def rrf_fusion(
    dense_results,
    bm25_results,
    k=60
):

    scores = defaultdict(float)

    chunk_lookup = {}

    for result in dense_results:

        child_id = result["child_id"]

        scores[child_id] += (
            1 / (k + result["rank"])
        )

        chunk_lookup[child_id] = result

    for result in bm25_results:

        child_id = result["child_id"]

        scores[child_id] += (
            1 / (k + result["rank"])
        )

        chunk_lookup[child_id] = result

    fused = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    final_results = []

    for child_id, score in fused:

        chunk = chunk_lookup[child_id]

        final_results.append(
            {
                "child_id": child_id,
                "parent_id": chunk["parent_id"],
                "text": chunk["text"],
                "rrf_score": score
            }
        )

    return final_results