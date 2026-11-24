from datetime import datetime, timezone
from sqlalchemy import String, Text, ForeignKey, DateTime, Integer, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

def utcnow(): return datetime.now(timezone.utc)
class Base(DeclarativeBase): pass
class Paper(Base):
    __tablename__ = 'papers'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(1000), index=True)
    year: Mapped[int | None] = mapped_column(Integer, index=True)
    doi: Mapped[str | None] = mapped_column(String(500), unique=True)
    abstract: Mapped[str] = mapped_column(Text, default='')
    access_level: Mapped[str] = mapped_column(String(30), default='manual_metadata')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (CheckConstraint('length(trim(title)) > 0'),)
class Collection(Base):
    __tablename__ = 'collections'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
class Membership(Base):
    __tablename__ = 'collection_papers'
    collection_id: Mapped[int] = mapped_column(ForeignKey('collections.id', ondelete='CASCADE'), primary_key=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey('papers.id', ondelete='CASCADE'), primary_key=True)
class Activity(Base):
    __tablename__ = 'activity'
    id: Mapped[int] = mapped_column(primary_key=True)
    event: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
