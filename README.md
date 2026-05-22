# Industry-Grade RAG Pipeline

A production-ready Retrieval-Augmented Generation (RAG) system built for scale. Upload PDFs through a web interface, have them automatically ingested into a vector store, and query them with a hybrid retrieval pipeline that combines dense and sparse search with cross-encoder reranking.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Ingestion Pipeline                        │
│                                                                  │
│   Upload UI  →  S3  →  SQS  →  ECS Worker  →  Pinecone         │
│   (HTML)         (eu-north-1)   (Fargate)       (Vector DB)     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        Retrieval Pipeline                        │
│                                                                  │
│   Query  →  Dense Search  ──┐                                   │
│                              ├──  Hybrid Search  →  Reranker    │
│          →  Sparse Search ──┘    (RRF Fusion)      (ONNX)      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Features

**Ingestion**
- PDF text extraction via PyMuPDF
- Sliding window chunking with configurable size and overlap
- Batched embedding generation via HuggingFace Inference API (`all-MiniLM-L6-v2`)
- Async S3 → SQS → ECS worker pipeline — non-blocking, event-driven
- Automatic retry via SQS Dead Letter Queue on failure
- Files moved from `uploads/` to `processed/` on success

**Retrieval**
- Dense retrieval via Pinecone vector similarity search
- Sparse retrieval via BM25 on locally cached chunks
- Hybrid fusion using Reciprocal Rank Fusion (RRF)
- Cross-encoder reranking via ONNX Runtime (`ms-marco-MiniLM-L-6-v2`) — no PyTorch dependency
- FastAPI REST endpoint for querying

**Infrastructure**
- Dockerized services with no CUDA/GPU dependencies
- Images hosted on Amazon ECR
- ECS Fargate — fully serverless, no EC2 management
- Corporate SSL proxy support (Zscaler compatible)
- Container Insights enabled for CPU/memory monitoring

---

## Project Structure

```
Industry-Grade-RAG/
│
├── ingestion-service/              # ECS Worker — S3 → Pinecone
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── worker.py                   # SQS long-polling worker
│   ├── append_cert.py              # Corporate CA cert injection
│   └── app/
│       ├── ssl_patch.py            # Zscaler SSL fix
│       └── ingestion/
│           ├── extractor.py        # PDF text extraction (PyMuPDF)
│           ├── chunker.py          # Sliding window chunker
│           ├── embedder.py         # HuggingFace API embeddings
│           ├── pipeline.py         # Orchestrates extraction → embedding → upload
│           └── vector_store.py     # Pinecone upsert + query
│
├── retrieval-service/              # FastAPI — Query endpoint
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py                 # FastAPI app
│       └── retrieval/
│           ├── dense_retriever.py  # Pinecone ANN search
│           ├── sparse_retriever.py # BM25 keyword search
│           ├── hybrid_retriever.py # RRF fusion
│           ├── reranker.py         # ONNX cross-encoder reranker
│           └── retriever.py        # Orchestrates full retrieval chain
│
└── upload.html                     # Minimal upload frontend
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| PDF Extraction | PyMuPDF |
| Chunking | Custom sliding window |
| Embeddings | HuggingFace Inference API (`all-MiniLM-L6-v2`) |
| Vector Store | Pinecone |
| Sparse Search | BM25 (rank-bm25) |
| Reranker | ONNX Runtime (`ms-marco-MiniLM-L-6-v2`) |
| API | FastAPI + Uvicorn |
| Queue | Amazon SQS |
| Storage | Amazon S3 |
| Container Registry | Amazon ECR |
| Compute | Amazon ECS Fargate |
| Monitoring | CloudWatch Container Insights |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker
- AWS CLI configured (`aws configure`)
- Pinecone account and index
- HuggingFace API key

### Environment Variables

Create a `.env` file in each service directory:

```env
# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name

# HuggingFace
HF_API_KEY=your_hf_api_key

# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=eu-north-1
S3_BUCKET_NAME=your_bucket_name
SQS_QUEUE_URL=https://sqs.eu-north-1.amazonaws.com/your_account_id/your_queue_name

# Python
PYTHONUNBUFFERED=1
```

### Run Locally

**Ingestion worker:**
```bash
cd ingestion-service
pip install -r requirements.txt
python worker.py
```

**Retrieval API:**
```bash
cd retrieval-service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Deploy to ECS

```bash
# Authenticate to ECR
aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.eu-north-1.amazonaws.com

# Build and push ingestion service
cd ingestion-service
docker build -t industry-rag/ingestion .
docker tag industry-rag/ingestion:latest YOUR_ACCOUNT_ID.dkr.ecr.eu-north-1.amazonaws.com/industry-rag/ingestion:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.eu-north-1.amazonaws.com/industry-rag/ingestion:latest

# Force ECS to pull new image
aws ecs update-service \
  --cluster industry-rag-cluster \
  --service ingestion-worker-service \
  --force-new-deployment \
  --region eu-north-1
```

---

## API

### Query endpoint

```
POST /query
Content-Type: application/json

{
  "query": "What is the attention mechanism?"
}
```

**Response:**
```json
{
  "results": [
    {
      "text": "...",
      "page": 4,
      "source": "paper.pdf",
      "rerank_score": 8.24
    }
  ]
}
```

---

## Retrieval Pipeline Detail

```
User Query
    │
    ├── Dense Retriever
    │   └── HuggingFace API → query embedding → Pinecone ANN → top-10 chunks
    │
    ├── Sparse Retriever
    │   └── BM25 on cached chunks → top-10 chunks
    │
    ├── Hybrid Fusion (RRF)
    │   └── Combines dense + sparse rankings → deduplicated top-10
    │
    └── Cross-Encoder Reranker (ONNX)
        └── Scores each (query, chunk) pair → returns top-5 reranked results
```

---

## Performance Comparison

Two ingestion worker variants are maintained for benchmarking:

| Variant | Image Tag | Description |
|---|---|---|
| Sync | `:sync` | Sequential processing — one stage completes before next begins |
| Async | `:async` | Concurrent processing — embedding batches overlap with I/O |

Metrics tracked via CloudWatch Container Insights:
- Total ingestion time per PDF
- CPU utilization during processing
- Memory peak
- Multi-PDF queue clearance time

---

## Monitoring

Enable Container Insights:
```bash
aws ecs update-cluster \
  --cluster industry-rag-cluster \
  --settings name=containerInsights,value=enabled \
  --region eu-north-1
```

View metrics:
```
CloudWatch → Container Insights → ECS Services → industry-rag-cluster
```

---

## Notes

- The reranker runs via ONNX Runtime — no PyTorch or CUDA required, keeping Docker images lean (~600MB vs 8GB with torch+CUDA)
- Embeddings are API-based (HuggingFace) — no model loaded in the container
- Corporate SSL proxies (Zscaler) are handled via cert injection into the certifi bundle at build time
- SQS Dead Letter Queue automatically catches failed ingestion jobs after 3 retries
