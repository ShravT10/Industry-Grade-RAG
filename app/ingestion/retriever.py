from app.ingestion.embedder import model
from app.ingestion.vector_store import query_pinecone


def retrieve_chunks(query, top_k=5):
    query_embedding = model.encode(query)

    results = query_pinecone(query_embedding, top_k=top_k)

    matches = []

    for match in results["matches"]:
        matches.append({
            "score": match["score"],
            "text": match["metadata"]["text"],
            "page": match["metadata"]["page"],
            "source": match["metadata"]["source"]
        })

    return matches