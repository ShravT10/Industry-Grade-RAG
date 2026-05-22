from app.retrieval.hybrid_retriever import hybrid_search
from app.retrieval.reranker import rerank_results


def retrieve_chunks(query):
    hybrid_results = hybrid_search(query)

    reranked_results = rerank_results(
        query,
        hybrid_results
    )

    return reranked_results