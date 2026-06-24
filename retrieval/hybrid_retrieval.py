from dense_retrieval import dense_search
from bm25_retrieval import bm25_search

from rrf import rrf_fusion

from reranker import rerank
from context_builder import build_context

TOP_K_DENSE = 20
TOP_K_BM25 = 20

def hybrid_search(
    query,
    dense_top_k=20,
    bm25_top_k=20
):

    dense_results = dense_search(
        query,
        dense_top_k
    )

    bm25_results = bm25_search(
        query,
        bm25_top_k
    )

    hybrid_results = rrf_fusion(
    dense_results,
    bm25_results
)

    top_chunks = rerank(
        query,
        hybrid_results,
        top_k=5
    )

    context = build_context(
        top_chunks
    )

    return {
        "top_chunks": top_chunks,
        "context": context
    }


