from celery import Celery
from app.database import SessionLocal
from app.models import Document, DocumentText
import pytesseract
from PIL import Image
import os

celery = Celery("worker", broker="pyamqp://guest@rabbitmq//")


@celery.task
def analyze_document_task(doc_id: int):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            file_path = os.path.join("documents", doc.filename)
            text = pytesseract.image_to_string(Image.open(file_path))
            doc_text = DocumentText(doc_id=doc.id, text=text)
            db.add(doc_text)
            db.commit()
    finally:
        db.close()