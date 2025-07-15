FROM python:3.9-slim


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    netcat-openbsd \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


ENV PYTHONPATH=/app \
    DOCUMENTS_DIR=/app/documents


RUN mkdir -p ${DOCUMENTS_DIR}
