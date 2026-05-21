# app/ingestion/vector_store.py
import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

_index = None


import asyncio

def get_index():
    global _index
    if _index is None:
        _index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    return _index


async def _upsert_batch(index, batch, batch_num, total_batches, semaphore):
    async with semaphore:
        print(f"Uploading Pinecone batch {batch_num} / {total_batches} (started)...")
        await asyncio.to_thread(index.upsert, vectors=batch)
        print(f"Uploaded Pinecone batch {batch_num} / {total_batches} (completed)")


async def upload_to_pinecone_async(chunks, embeddings, document_name, batch_size=100, max_concurrency=4):
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

    if not vectors:
        return

    index = get_index()
    total_batches = (len(vectors) + batch_size - 1) // batch_size
    semaphore = asyncio.Semaphore(max_concurrency)

    tasks = []
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        batch_num = i // batch_size + 1
        tasks.append(
            _upsert_batch(index, batch, batch_num, total_batches, semaphore)
        )

    await asyncio.gather(*tasks)
    print(f"Uploaded {len(vectors)} vectors to Pinecone")


def upload_to_pinecone(chunks, embeddings, document_name):
    # Backward compatible synchronous wrapper
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                lambda: asyncio.run(
                    upload_to_pinecone_async(chunks, embeddings, document_name)
                )
            )
            future.result()
    else:
        asyncio.run(upload_to_pinecone_async(chunks, embeddings, document_name))


def query_pinecone(query_embedding, top_k=5):
    results = get_index().query(
        vector=query_embedding.tolist(),
        top_k=top_k,
        include_metadata=True
    )
    return results


async def query_pinecone_async(query_embedding, top_k=5):
    return await asyncio.to_thread(query_pinecone, query_embedding, top_k)