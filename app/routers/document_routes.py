from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Document, DocumentText
from app.celery_worker import analyze_document_task
import os
import shutil

router = APIRouter()

DOCUMENTS_DIR = "/app/documents"
os.makedirs(DOCUMENTS_DIR, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload_doc", summary="Загрузить документ")
def upload_doc(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Загрузка документа в FastAPI"""
    try:
        # Сохранение файла
        file_path = os.path.join(DOCUMENTS_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Сохранение в БД
        doc = Document(filename=file.filename)
        db.add(doc)
        db.commit()
        db.refresh(doc)

        print(f"Файл {file.filename} успешно загружен, ID: {doc.id}")
        return {"doc_id": doc.id, "message": "Файл успешно загружен"}

    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {str(e)}")


@router.delete("/doc_delete", summary="Удалить документ")
def doc_delete(doc_id: int, db: Session = Depends(get_db)):
    """Удаление документа"""
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        file_path = os.path.join(DOCUMENTS_DIR, doc.filename)

        # Удаление из БД
        db.delete(doc)
        db.commit()

        # Удаление файла
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Файл {file_path} удален")

        return {"detail": "Документ успешно удален!"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка при удалении документа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении: {str(e)}")


@router.post("/doc_analyse", summary="Анализ документа")
def doc_analyse(doc_id: int, db: Session = Depends(get_db)):
    """Запуск анализа документа"""
    try:
        # Проверяем, что документ существует
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Запускаем задачу анализа
        analyze_document_task.delay(doc_id)
        print(f"Анализ документа {doc_id} запущен")

        return {"detail": "Задача анализа запущена"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка при запуске анализа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при запуске анализа: {str(e)}")


@router.get("/get_text", summary="Получить текст")
def get_text(doc_id: int, db: Session = Depends(get_db)):
    """Получение распознанного текста"""
    try:
        # Проверяем, что документ существует
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Получаем текст
        text_record = db.query(DocumentText).filter(DocumentText.doc_id == doc_id).first()
        text = text_record.text if text_record else ""

        print(f"Текст для документа {doc_id}: {len(text)} символов")
        return {"text": text}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка при получении текста: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении текста: {str(e)}")


@router.get("/documents", summary="Список всех документов")
def list_documents(db: Session = Depends(get_db)):
    """Получение списка всех документов"""
    try:
        documents = db.query(Document).all()
        return {
            "documents": [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "has_text": bool(db.query(DocumentText).filter(DocumentText.doc_id == doc.id).first())
                }
                for doc in documents
            ]
        }
    except Exception as e:
        print(f"Ошибка при получении списка документов: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении списка: {str(e)}")