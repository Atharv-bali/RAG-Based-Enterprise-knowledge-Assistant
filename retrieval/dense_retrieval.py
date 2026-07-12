import json
# Converts text into embeddings
from sentence_transformers import SentenceTransformer

# Qdrant is a vector database
from qdrant_client import QdrantClient

# Imports distance matrix to find optimal distance between vectors
from qdrant_client.models import Distance
from qdrant_client.models import VectorParams
from qdrant_client.models import PointStruct

COLLECTION_NAME = "child_chunks"

CHILD_CHUNKS_PATH = "output/child_chunks.json"

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

TOP_K = 10

# Loads the embedding model and creates a Qdrant collection for storing embeddings
print("Loading embedding model...")

model = SentenceTransformer(EMBEDDING_MODEL)

embedding_dim = model.get_embedding_dimension()

print("Embedding dimension:", embedding_dim)

# Creating the collection inside the database to store embeddings
client = QdrantClient(":memory:")

last_loaded_mtime = 0

def ensure_collection_loaded():
    global last_loaded_mtime
    import os
    if not os.path.exists(CHILD_CHUNKS_PATH):
        return
        
    try:
        mtime = os.path.getmtime(CHILD_CHUNKS_PATH)
    except OSError:
        return
        
    if mtime == last_loaded_mtime:
        return
        
    print("Loading child chunks and generating embeddings in Qdrant...")
    try:
        with open(CHILD_CHUNKS_PATH, "r", encoding="utf-8") as f:
            child_chunks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=embedding_dim,
            distance=Distance.COSINE
        )
    )

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

    if points:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        print(f"Loaded and indexed {len(points)} chunks in Qdrant.")
        last_loaded_mtime = mtime
    else:
        print("No chunks found to index in Qdrant.")

# Initialize collection if child chunks already exist at startup
try:
    ensure_collection_loaded()
except Exception as e:
    print(f"Warning: Could not initialize Qdrant database: {e}")


def dense_search(query, top_k=TOP_K):
    ensure_collection_loaded()
    
    try:
        collection_info = client.get_collection(collection_name=COLLECTION_NAME)
        if collection_info.points_count == 0:
            return []
    except Exception:
        return []

    query_vector = model.encode(query).tolist()
    # Finding similar embeddings
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