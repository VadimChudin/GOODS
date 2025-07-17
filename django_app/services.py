import requests
from django.conf import settings
from requests.exceptions import RequestException
import time


class FastAPIService:
    @staticmethod
    def analyze_document(doc_id):
        """Отправка документа на анализ в FastAPI"""
        try:
            response = requests.post(
                f"{settings.FASTAPI_URL}/doc_analyse",
                params={'doc_id': doc_id},  # Используем params вместо json
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {'detail': f'Ошибка анализа: {response.text}'}
        except RequestException as e:
            return {'detail': f'Ошибка соединения: {str(e)}'}

    @staticmethod
    def get_text(doc_id):
        """Получение распознанного текста из FastAPI"""
        # Ждем немного, чтобы анализ успел завершиться
        time.sleep(2)

        try:
            response = requests.get(
                f"{settings.FASTAPI_URL}/get_text",
                params={'doc_id': doc_id},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {'text': '', 'error': f'Ошибка получения текста: {response.text}'}
        except RequestException as e:
            return {'text': '', 'error': f'Ошибка соединения: {str(e)}'}

    @staticmethod
    def delete_document(doc_id):
        """Удаление документа через FastAPI"""
        try:
            response = requests.delete(
                f"{settings.FASTAPI_URL}/doc_delete",
                params={'doc_id': doc_id},
                timeout=30
            )
            return response.status_code == 200
        except RequestException as e:
            print(f"Ошибка при удалении документа в FastAPI: {e}")
            return False