from app.retrieval.dense_retriever import dense_search
from app.retrieval.sparse_retriever import sparse_search


def hybrid_search(query):
    dense_results = dense_search(query)
    sparse_results = sparse_search(query)

    combined = {}

    for result in dense_results + sparse_results:
        combined[result["id"]] = result

    return list(combined.values())