FROM python:3.11-slim

WORKDIR /app

COPY company-ca.crt /tmp/company-ca.pem

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates openssl && \
    cp /tmp/company-ca.pem /usr/local/share/ca-certificates/company-ca.crt && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV HTTPX_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

RUN pip config set global.trusted-host \
    "pypi.org files.pythonhosted.org download.pytorch.org download-r2.pytorch.org"

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir \
    fastapi uvicorn pymupdf pinecone \
    python-dotenv rank-bm25 numpy \
    python-multipart requests \
    onnxruntime==1.19.2 transformers certifi

RUN pip install --no-cache-dir --no-deps optimum optimum-onnx

RUN pip uninstall -y \
    torch torchvision torchaudio triton \
    cuda-bindings cuda-pathfinder cuda-toolkit \
    nvidia-cublas nvidia-cuda-cupti nvidia-cuda-nvrtc \
    nvidia-cuda-runtime nvidia-cudnn-cu13 nvidia-cufft \
    nvidia-cufile nvidia-curand nvidia-cusolver \
    nvidia-cusparse nvidia-cusparselt-cu13 nvidia-nccl-cu13 \
    nvidia-nvjitlink nvidia-nvshmem-cu13 nvidia-nvtx \
    2>/dev/null || true

# Write the append script to a file first, then run it
COPY append_cert.py /tmp/append_cert.py
RUN python3 /tmp/append_cert.py

COPY app/models ./app/models
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]