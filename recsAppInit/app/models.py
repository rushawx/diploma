"""
Database models for initialization service
"""

import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    String,
    Text,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

from config import settings

Base = declarative_base()


class User(Base):
    """User model for admin operations"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True)
    nick_name = Column(String(128), nullable=False, unique=True)
    password = Column(String, nullable=False)
    user_type = Column(String(50), default="student")
    created_at = Column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
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
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=False)
    tags = Column(Vector(settings.TAGS_VECTOR_DIMENSION), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    modified_by = Column(UUID(as_uuid=True), nullable=True)
    chosen_by = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"<Project(id={self.id}, title_rus='{self.title_rus}')>"


class Rating(Base):
    """Rating model for collaborative filtering"""

    __tablename__ = "ratings"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )

    user = relationship("User", backref="ratings")
    project = relationship("Project", backref="ratings")

    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="unique_user_project_rating"),
    )

    def __repr__(self):
        return f"<Rating(id={self.id}, user_id={self.user_id}, project_id={self.project_id}, rating={self.rating})>"
