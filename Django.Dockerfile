FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование и установка зависимостей
COPY requirements-django.txt .
RUN pip install --no-cache-dir -r requirements-django.txt

# Копирование кода приложения
COPY . .

# Создание директории для медиа файлов
RUN mkdir -p /app/media

# Применение миграций и запуск сервера
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]