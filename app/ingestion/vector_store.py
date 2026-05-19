import os
import json
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

CHUNK_FILE = os.path.join(BASE_DIR, "data", "chunks.json")


def save_chunks_locally(chunks, document_name):
    existing_chunks = []

    if os.path.exists(CHUNK_FILE):
        try:
            with open(CHUNK_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()

                if content:
                    existing_chunks = json.loads(content)

        except json.JSONDecodeError:
            existing_chunks = []

    for i, chunk in enumerate(chunks):
        existing_chunks.append({
            "id": f"{document_name}-{i}",
            "text": chunk["text"],
            "page": chunk["page"],
            "source": document_name
        })

    with open(CHUNK_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_chunks, f, indent=2)

    print(f"Saved {len(chunks)} chunks locally")


def upload_to_pinecone(chunks, embeddings, document_name):
    vectors = []

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        vector = {
            "id": f"{document_name}-{i}",
            "values": embedding.tolist(),
            "metadata": {
                "text": chunk["text"],
                "page": chunk["page"],
                "source": document_name
            }
        }

        vectors.append(vector)

    index.upsert(vectors=vectors)
    save_chunks_locally(chunks, document_name)



def query_pinecone(query_embedding, top_k=5):
    results = index.query(
        vector=query_embedding.tolist(),
        top_k=top_k,
        include_metadata=True
    )

    return results