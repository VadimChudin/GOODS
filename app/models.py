from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True)
    texts = relationship("DocumentText", backref="document", cascade="all, delete")

class DocumentText(Base):
    __tablename__ = 'document_texts'
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id"))
    text = Column(String)