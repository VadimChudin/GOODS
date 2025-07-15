import requests
from django.conf import settings


class FastAPIService:
    """Сервис для работы с FastAPI"""

    def __init__(self):
        self.base_url = settings.FASTAPI_SERVICE_URL

    def upload_document(self, file, filename):
        """Загрузка документа в FastAPI"""
        url = f"{self.base_url}/upload_doc"
        files = {'file': (filename, file, 'image/jpeg')}

        response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()

    def delete_document(self, doc_id):
        """Удаление документа из FastAPI"""
        url = f"{self.base_url}/doc_delete"
        params = {'doc_id': doc_id}

        response = requests.delete(url, params=params)
        response.raise_for_status()
        return response.json()

    def analyze_document(self, doc_id):
        """Анализ документа в FastAPI"""
        url = f"{self.base_url}/doc_analyse"
        data = {'doc_id': doc_id}

        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def get_text(self, doc_id):
        """Получение текста документа из FastAPI"""
        url = f"{self.base_url}/get_text"
        params = {'doc_id': doc_id}

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()