# app/retrieval/dense_retriever.py
import os
import requests
import numpy as np
from dotenv import load_dotenv
from app.ingestion.vector_store import query_pinecone

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
MODEL_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}


def embed_query(query: str) -> np.ndarray:
    response = requests.post(
        MODEL_URL,
        headers=HEADERS,
        json={
            "inputs": query,
            "options": {"wait_for_model": True}
        }
    )
    response.raise_for_status()
    return np.array(response.json())


def dense_search(query, top_k=10):
    query_embedding = embed_query(query)

    results = query_pinecone(query_embedding, top_k=top_k)

    matches = []
    for match in results["matches"]:
        matches.append({
            "id": match["id"],
            "score": match["score"],
            "text": match["metadata"]["text"],
            "page": match["metadata"]["page"],
            "source": match["metadata"]["source"]
        })

    return matches