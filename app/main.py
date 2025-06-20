from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
import os
import base64
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Document, DocumentText, Base
from app.celery_worker import analyze_document_task
from typing import Optional


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Processing API",
    description="API for uploading, analyzing and retrieving documents",
    version="1.0.0"
)


os.makedirs("documents", exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/upload_doc',
          summary="Upload document",
          description="Uploads a file in binary or base64 format and saves it to database",
          response_description="Returns document ID and filename")
async def upload_document(
        file: Optional[UploadFile] = File(None),
        b64_data: Optional[str] = Form(None),
        filename: Optional[str] = Form(None),
        db: Session = Depends(get_db)
):
    try:
        if file:
            file_location = f'documents/{file.filename}'
            with open(file_location, 'wb+') as file_object:
                file_object.write(await file.read())
            filename = file.filename
        elif b64_data and filename:
            file_location = f'documents/{filename}'
            with open(file_location, 'wb') as f:
                f.write(base64.b64decode(b64_data))
        else:
            raise HTTPException(
                status_code=400,
                detail="Either file or b64_data with filename must be provided"
            )

        db_document = Document(path=file_location)
        db.add(db_document)
        db.commit()
        db.refresh(db_document)

        return {'id': db_document.id, 'filename': filename}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.delete('/doc_delete',
            summary="Delete document",
            description="Deletes a document from server and database",
            response_description="Confirmation message")
async def delete_document(
        document_id: int,
        db: Session = Depends(get_db)
):
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail='Document not found')

        if os.path.exists(document.path):
            os.remove(document.path)

        db.query(DocumentText).filter(DocumentText.id_doc == document_id).delete()
        db.delete(document)
        db.commit()

        return {'message': 'File deleted successfully'}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.post('/doc_analyse',
          summary="Analyze document",
          description="Starts background processing of document using OCR",
          response_description="Task status")
async def analyze_document(
        document_id: int,
        db: Session = Depends(get_db)
):
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail='Document not found')

        if not os.path.exists(document.path):
            raise HTTPException(status_code=404, detail='File not found on disk')

        analyze_document_task.delay(document_id)
        return {'message': 'Document sent for processing'}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/get_text',
         summary="Get document text",
         description="Retrieves extracted text from processed document",
         response_description="Document text")
async def get_text(
        document_id: int,
        db: Session = Depends(get_db)
):
    try:
        document_text = db.query(DocumentText).filter(DocumentText.id_doc == document_id).first()
        if not document_text:
            raise HTTPException(status_code=404, detail='Text not found for this document')

        return {'text': document_text.text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))