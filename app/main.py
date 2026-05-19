import os

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

from app.retrieval.retriever import retrieve_chunks
from app.ingestion.pipeline import ingest_pdf

class QueryRequest(BaseModel):
    query: str

app = FastAPI()


UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    ingest_pdf(file_path, file.filename)

    return {
        "message": "PDF ingested successfully",
        "file": file.filename
    }

@app.post("/query")
async def query_documents(request: QueryRequest):
    results = retrieve_chunks(request.query)

    return {
        "query": request.query,
        "results": results
    }