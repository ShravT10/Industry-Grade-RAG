FROM python:3.11-slim

WORKDIR /app

RUN pip config set global.trusted-host \
    "pypi.org files.pythonhosted.org download.pytorch.org download-r2.pytorch.org"

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip

# Install everything except torch
RUN pip install --no-cache-dir -r requirements.txt

# Explicitly uninstall torch if it sneaked in as a transitive dependency
RUN pip uninstall -y torch torchvision torchaudio 2>/dev/null || true

COPY app/models ./app/models
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]