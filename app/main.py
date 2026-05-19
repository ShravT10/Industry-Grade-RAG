import os

from fastapi import FastAPI, UploadFile, File

from app.ingestion.pipeline import ingest_pdf

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