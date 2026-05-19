import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))


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

def query_pinecone(query_embedding, top_k=5):
    results = index.query(
        vector=query_embedding.tolist(),
        top_k=top_k,
        include_metadata=True
    )

    return results