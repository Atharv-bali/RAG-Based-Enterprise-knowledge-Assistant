import json

PARENT_PATH = "output/parent_chunks.json"

with open(
    PARENT_PATH,
    "r",
    encoding="utf-8"
) as f:

    parent_chunks = json.load(f)

parent_lookup = {}

for parent in parent_chunks:

    parent_lookup[
        parent["parent_id"]
    ] = parent["text"]


def build_context(
    reranked_chunks
):

    context_parts = []

    seen_parents = set()

    for chunk in reranked_chunks:

        parent_id = chunk["parent_id"]

        if parent_id in seen_parents:
            continue

        seen_parents.add(parent_id)

        parent_text = parent_lookup[
            parent_id
        ]

        context_parts.append(
            parent_text
        )

    return "\n\n".join(
        context_parts
    )