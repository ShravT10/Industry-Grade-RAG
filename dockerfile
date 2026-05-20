FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir \
        torch==2.3.1+cpu \
        torchvision==0.18.1+cpu \
        --index-url https://download.pytorch.org/whl/cpu \
        --trusted-host download.pytorch.org \
        --trusted-host download-r2.pytorch.org \
        --trusted-host pypi.org \
        --trusted-host files.pythonhosted.org

RUN pip install --no-cache-dir \
        transformers==4.41.2 \
        sentence-transformers==3.0.1

RUN pip install --no-cache-dir -r requirements.txt \
        --trusted-host pypi.org \
        --trusted-host files.pythonhosted.org

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]