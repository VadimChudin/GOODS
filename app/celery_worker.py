from celery import Celery
from app.database import SessionLocal
from app.models import Document, DocumentText
import pytesseract
from PIL import Image
import os

celery = Celery("worker", broker="pyamqp://guest@rabbitmq//")

DOCUMENTS_DIR = "/app/documents"


@celery.task
def analyze_document_task(doc_id: int):
    """Задача для анализа документа через OCR"""
    db = SessionLocal()
    try:
        print(f"Начинаю анализ документа {doc_id}")

        # Получаем документ из БД
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            print(f"Документ {doc_id} не найден")
            return {"status": "error", "message": "Document not found"}

        # Проверяем, есть ли уже текст для этого документа
        existing_text = db.query(DocumentText).filter(DocumentText.doc_id == doc_id).first()
        if existing_text:
            print(f"Текст для документа {doc_id} уже существует, перезаписываем")
            db.delete(existing_text)
            db.commit()

        # Путь к файлу
        file_path = os.path.join(DOCUMENTS_DIR, doc.filename)

        if not os.path.exists(file_path):
            print(f"Файл {file_path} не найден")
            return {"status": "error", "message": "File not found"}

        print(f"Анализирую файл: {file_path}")

        # Распознавание текста
        try:
            # Настройки для tesseract
            config = '--psm 6 -l rus+eng'  # Автоматическое определение структуры + русский и английский

            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, config=config)

            print(f"Распознано {len(text)} символов")

            # Сохраняем результат в БД
            doc_text = DocumentText(doc_id=doc.id, text=text)
            db.add(doc_text)
            db.commit()

            print(f"Текст для документа {doc_id} успешно сохранен")
            return {"status": "success", "text_length": len(text)}

        except Exception as e:
            print(f"Ошибка при распознавании текста: {e}")
            return {"status": "error", "message": f"OCR error: {str(e)}"}

    except Exception as e:
        print(f"Общая ошибка при анализе документа {doc_id}: {e}")
        return {"status": "error", "message": str(e)}

    finally:
        db.close()