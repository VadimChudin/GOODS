FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    postgresql-client \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-rus \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements-fastapi.txt .
RUN pip install --no-cache-dir -r requirements-fastapi.txt
COPY . .

RUN mkdir -p /app/documents

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]