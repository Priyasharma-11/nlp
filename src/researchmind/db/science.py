from sqlalchemy import ForeignKey, String, Text, Integer, LargeBinary, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .models import Base

class SourceRecord(Base):
    __tablename__ = 'source_records'
    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey('papers.id', ondelete='CASCADE'), index=True)
    provider: Mapped[str] = mapped_column(String(40))
    external_id: Mapped[str] = mapped_column(Text)
    retrieved_at: Mapped[str] = mapped_column(String(40))
    normalized: Mapped[str] = mapped_column(Text)
    raw: Mapped[str] = mapped_column(Text)
    __table_args__ = (UniqueConstraint('provider','external_id'),)

class Document(Base):
    __tablename__ = 'documents'
    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey('papers.id', ondelete='CASCADE'), index=True)
    sha256: Mapped[str] = mapped_column(String(64), unique=True)
    filename: Mapped[str] = mapped_column(Text)
    uploaded_at: Mapped[str] = mapped_column(String(40))
    original: Mapped[bytes] = mapped_column(LargeBinary)
    metadata_json: Mapped[str] = mapped_column(Text)

class Passage(Base):
    __tablename__ = 'passages'
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id', ondelete='CASCADE'), index=True)
    page: Mapped[int] = mapped_column(Integer)
    ordinal: Mapped[int] = mapped_column(Integer)
    section: Mapped[str] = mapped_column(String(80))
    text: Mapped[str] = mapped_column(Text)
    bbox_json: Mapped[str] = mapped_column(Text)
    __table_args__ = (UniqueConstraint('document_id','page','ordinal'),)
