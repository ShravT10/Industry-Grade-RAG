from app.ingestion.extractor import extract_text_from_pdf
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import generate_embeddings
from app.ingestion.vector_store import upload_to_pinecone


def ingest_pdf(pdf_path, document_name):
    print("Extracting text...")

    pages = extract_text_from_pdf(pdf_path)

    print("Chunking text...")

    chunks = chunk_text(pages)

    print(f"Generated {len(chunks)} chunks")

    print("Generating embeddings...")

    embeddings = generate_embeddings(chunks)

    print("Uploading to Pinecone...")

    upload_to_pinecone(chunks, embeddings, document_name)

    print("Ingestion completed")