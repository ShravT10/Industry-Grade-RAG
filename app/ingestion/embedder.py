# embedder.py
import os
import requests
import numpy as np
from dotenv import load_dotenv
model = ''
load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
MODEL_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}


def generate_embeddings(chunks, batch_size=32):
    texts = [chunk["text"] for chunk in chunks]
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]

        print(f"Embedding batch {i // batch_size + 1} / {(len(texts) + batch_size - 1) // batch_size}")

        response = requests.post(
            MODEL_URL,
            headers=HEADERS,
            json={
                "inputs": batch,
                "options": {"wait_for_model": True}
            }
        )

        response.raise_for_status()

        all_embeddings.extend(response.json())

    return np.array(all_embeddings)