# app/ingestion/vector_store.py
import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

_index = None


def get_index():
    global _index
    if _index is None:
        _index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    return _index


def upload_to_pinecone(chunks, embeddings, document_name):
    vectors = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        vectors.append({
            "id": f"{document_name}-{i}",
            "values": embedding.tolist(),
            "metadata": {
                "text": chunk["text"],
                "page": chunk["page"],
                "source": document_name
            }
        })
    get_index().upsert(vectors=vectors)
    print(f"Uploaded {len(vectors)} vectors to Pinecone")


def query_pinecone(query_embedding, top_k=5):
    results = get_index().query(
        vector=query_embedding.tolist(),
        top_k=top_k,
        include_metadata=True
    )
    return results