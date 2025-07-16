import requests
from django.conf import settings
from requests.exceptions import RequestException

class FastAPIService:
    @staticmethod
    def analyze_document(doc_id):
        """Отправка документа на анализ в FastAPI"""
        try:
            response = requests.post(
                f"{settings.FASTAPI_URL}/doc_analyse",
                json={'doc_id': doc_id},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {'status': 'error', 'message': str(e)}

    @staticmethod
    def get_text(doc_id):
        """Получение распознанного текста из FastAPI"""
        try:
            response = requests.get(
                f"{settings.FASTAPI_URL}/get_text",
                params={'doc_id': doc_id},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {'text': '', 'error': str(e)}

    @staticmethod
    def delete_document(doc_id):
        """Удаление документа через FastAPI"""
        try:
            response = requests.delete(
                f"{settings.FASTAPI_URL}/doc_delete",
                params={'doc_id': doc_id},
                timeout=10
            )
            response.raise_for_status()
            return True
        except RequestException:
            return False