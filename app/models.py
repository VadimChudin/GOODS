from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from app.database import Base


class Document(Base):
    __tablename__ = 'Documents'

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String)
    date = Column(DateTime, default=func.now())


class DocumentText(Base):
    __tablename__ = 'Documents_text'
    id = Column(Integer, primary_key=True, index=True)
    id_doc = Column(Integer, ForeignKey('Documents.id'), index=True)
    text = Column(Text)
    processed_at = Column(DateTime, default=func.now())