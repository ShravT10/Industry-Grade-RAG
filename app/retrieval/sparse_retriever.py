import json
import os

from rank_bm25 import BM25Okapi


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

CHUNK_FILE = os.path.join(BASE_DIR, "data", "chunks.json")


def load_chunks():
    print(f"Loading chunks from: {CHUNK_FILE}")

    if not os.path.exists(CHUNK_FILE):
        print("Chunks file does not exist")
        return []

    with open(CHUNK_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()

        print("Raw file content:")
        print(content[:500])

        if not content:
            print("Chunks file is empty")
            return []

        chunks = json.loads(content)

        print(f"Loaded {len(chunks)} chunks")

        return chunks


def sparse_search(query, top_k=10):
    chunks = load_chunks()

    corpus = [chunk["text"] for chunk in chunks]

    tokenized_corpus = [doc.split() for doc in corpus]
    print(f"Corpus size: {len(tokenized_corpus)}")
    
    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_query = query.split()

    scores = bm25.get_scores(tokenized_query)

    scored_chunks = []

    for chunk, score in zip(chunks, scores):
        scored_chunks.append({
            "id": chunk["id"],
            "score": float(score),
            "text": chunk["text"],
            "page": chunk["page"],
            "source": chunk["source"]
        })

    scored_chunks.sort(key=lambda x: x["score"], reverse=True)

    return scored_chunks[:top_k]