from app.ingestion.extractor import extract_text_from_pdf
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import generate_embeddings, generate_embeddings_async
from app.ingestion.vector_store import upload_to_pinecone, upload_to_pinecone_async
import asyncio


async def ingest_pdf_async(pdf_path, document_name):
    print("Extracting text...")
    # Run CPU-bound extractor in a thread pool to avoid blocking the event loop
    pages = await asyncio.to_thread(extract_text_from_pdf, pdf_path)

    print("Chunking text...")
    chunks = await asyncio.to_thread(chunk_text, pages)

    print(f"Generated {len(chunks)} chunks")

    print("Generating embeddings...")
    embeddings = await generate_embeddings_async(chunks)

    print("Uploading to Pinecone...")
    await upload_to_pinecone_async(chunks, embeddings, document_name)

    print("Ingestion completed")


def ingest_pdf(pdf_path, document_name):
    # Backward compatible synchronous wrapper
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                lambda: asyncio.run(ingest_pdf_async(pdf_path, document_name))
            )
            future.result()
    else:
        asyncio.run(ingest_pdf_async(pdf_path, document_name))