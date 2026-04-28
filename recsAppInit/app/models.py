"""
Database models for initialization service
"""
import datetime
from sqlalchemy import Column, DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class User(Base):
    """User model for admin operations"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True)
    nick_name = Column(String(128), nullable=False, unique=True)
    password = Column(String, nullable=False)
    user_type = Column(String(50), default='student')
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, nick_name='{self.nick_name}')>"


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
