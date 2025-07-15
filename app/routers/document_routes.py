from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Document, DocumentText
from app.celery_worker import analyze_document_task
import os
import shutil

router = APIRouter()

DOCUMENTS_DIR = "documents"
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload_doc", summary="Загрузить документ")
def upload_doc(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = os.path.join(DOCUMENTS_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc = Document(filename=file.filename)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"doc_id": doc.id}

@router.delete("/doc_delete", summary="Удалить документ")
def doc_delete(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    file_path = os.path.join(DOCUMENTS_DIR, doc.filename)

    db.delete(doc)
    db.commit()
    if os.path.exists(file_path):
        os.remove(file_path)
    return {"detail": "документ успешно удален!"}

@router.post("/doc_analyse", summary="Анализ документа")
def doc_analyse(doc_id: int):
    analyze_document_task.delay(doc_id)
    return {"detail": "Task started"}

@router.get("/get_text", summary="Получить текст")
def get_text(doc_id: int, db: Session = Depends(get_db)):
    text = db.query(DocumentText).filter(DocumentText.doc_id == doc_id).first()
    return {"text": text.text if text else ""}

