from celery import Celery
import pytesseract
from PIL import Image
from app.models import Document, DocumentText
from app.database import SessionLocal
import os

app = Celery(
    'tasks',
    broker='amqp://guest@rabbitmq//',
    broker_connection_retry_on_startup=True
)


@app.task(bind=True, max_retries=3)
def analyze_document_task(self, document_id):
    db = SessionLocal()
    try:
        doc = db.query(Document).get(document_id)
        if not doc:
            raise ValueError(f"Document {document_id} not found")

        if not os.path.exists(doc.path):
            raise FileNotFoundError(f"File {doc.path} missing")

        text = pytesseract.image_to_string(Image.open(doc.path))
        if not text.strip():
            raise ValueError("No text recognized")

        existing = db.query(DocumentText).filter_by(id_doc=document_id).first()
        if existing:
            existing.text = text
        else:
            db.add(DocumentText(id_doc=document_id, text=text))

        db.commit()
        return {"status": "success", "document_id": document_id}

    except Exception as e:
        db.rollback()
        raise self.retry(exc=e)
    finally:
        db.close()