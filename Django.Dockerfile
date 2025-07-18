FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-django.txt .
RUN pip install --no-cache-dir -r requirements-django.txt

COPY . .

RUN mkdir -p /app/media

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]