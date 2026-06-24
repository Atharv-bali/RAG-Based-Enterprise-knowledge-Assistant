import json

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance
from qdrant_client.models import VectorParams
from qdrant_client.models import PointStruct

COLLECTION_NAME = "child_chunks"

CHILD_CHUNKS_PATH = "output/child_chunks.json"

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

TOP_K = 10

print("Loading embedding model...")

model = SentenceTransformer(EMBEDDING_MODEL)

embedding_dim = model.get_embedding_dimension()

print("Embedding dimension:", embedding_dim)

client = QdrantClient(":memory:")

client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=embedding_dim,
        distance=Distance.COSINE
    )
)

print("Qdrant collection created")

with open(CHILD_CHUNKS_PATH, "r", encoding="utf-8") as f:
    child_chunks = json.load(f)

print("Loaded child chunks:", len(child_chunks))

points = []

for idx, chunk in enumerate(child_chunks):

    text = chunk["text"]

    vector = model.encode(text).tolist()

    points.append(
        PointStruct(
            id=idx,
            vector=vector,
            payload={
                "child_id": chunk["child_id"],
                "parent_id": chunk["parent_id"],
                "text": text
            }
        )
    )

print("Generated embeddings")

client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)

print("Inserted into Qdrant")

def dense_search(query, top_k=TOP_K):

    query_vector = model.encode(query).tolist()

    hits = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    ).points

    results = []

    for rank, hit in enumerate(hits, start=1):

        results.append(
            {
                "child_id": hit.payload["child_id"],
                "parent_id": hit.payload["parent_id"],
                "text": hit.payload["text"],
                "rank": rank,
                "score": float(hit.score)
            }
        )

    return results

if __name__ == "__main__":

    query = "From where did loreum epsom come?"

    results = dense_search(query)

    print("\nSEARCH RESULTS\n")

    for result in results:

        print("=" * 60)

        print("Rank:", result["rank"])

        print("Score:", round(result["score"], 4))

        print("Child ID:", result["child_id"])

        print("Parent ID:", result["parent_id"])

        print(result["text"][:500])