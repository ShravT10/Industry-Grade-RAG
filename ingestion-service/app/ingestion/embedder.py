import os
import requests
import numpy as np
import httpx
import asyncio
from dotenv import load_dotenv
model = ''
load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
MODEL_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}


async def _embed_batch(client, batch, batch_num, total_batches, semaphore):
    async with semaphore:
        print(f"Embedding batch {batch_num} / {total_batches} (started)...")
        response = await client.post(
            MODEL_URL,
            headers=HEADERS,
            json={
                "inputs": batch,
                "options": {"wait_for_model": True}
            },
            timeout=60.0
        )
        response.raise_for_status()
        print(f"Embedding batch {batch_num} / {total_batches} (completed)")
        return response.json()


async def generate_embeddings_async(chunks, batch_size=32, max_concurrency=5):
    texts = [chunk["text"] for chunk in chunks]
    if not texts:
        return np.array([])

    total_batches = (len(texts) + batch_size - 1) // batch_size
    semaphore = asyncio.Semaphore(max_concurrency)

    async with httpx.AsyncClient() as client:
        tasks = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_num = i // batch_size + 1
            tasks.append(
                _embed_batch(client, batch, batch_num, total_batches, semaphore)
            )

        results = await asyncio.gather(*tasks)

    all_embeddings = []
    for batch_embeddings in results:
        all_embeddings.extend(batch_embeddings)

    return np.array(all_embeddings)


def generate_embeddings(chunks, batch_size=32):
    # Backward compatible synchronous wrapper
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Running inside an existing event loop.
        # Run in a separate thread to avoid blocking the event loop or causing a RuntimeError.
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                lambda: asyncio.run(generate_embeddings_async(chunks, batch_size))
            )
            return future.result()
    else:
        return asyncio.run(generate_embeddings_async(chunks, batch_size))