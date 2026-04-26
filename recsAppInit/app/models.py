"""
Database models for initialization service
"""
import datetime
from sqlalchemy import Column, DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class Project(Base):
    """Project model for recommendations"""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True)
    title_rus = Column(String(512), nullable=False)
    title_eng = Column(String(512), nullable=True)
    annotation = Column(Text(), nullable=False)
    description = Column(Text(), nullable=False)
    embedding = Column(Vector(384), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    modified_by = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"<Project(id={self.id}, title_rus='{self.title_rus}')>"
