from fastapi import FastAPI
from pydantic import BaseModel

from app.retrieval.retriever import retrieve_chunks

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def query_documents(request: QueryRequest):
    results = retrieve_chunks(request.query)

    return {
        "query": request.query,
        "results": results
    }