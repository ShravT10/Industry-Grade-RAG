from sentence_transformers import CrossEncoder


reranker_model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank_results(query, results, top_k=5):
    pairs = []

    for result in results:
        pairs.append((query, result["text"]))

    scores = reranker_model.predict(pairs)

    reranked = []

    for result, score in zip(results, scores):
        result["rerank_score"] = float(score)

        reranked.append(result)

    reranked.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return reranked[:top_k]