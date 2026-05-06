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
    self_bio = Column(String, unique=False)
    avatar_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
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


class Tag(Base):
    """Tag model for storing available tags"""

    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"


class UserTag(Base):
    """User-Tag association model"""

    __tablename__ = "user_tags"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )

    user = relationship("User", backref="user_tags")
    tag = relationship("Tag", backref="user_tags")

    __table_args__ = (
        UniqueConstraint("user_id", "tag_id", name="unique_user_tag"),
    )

    def __repr__(self):
        return f"<UserTag(id={self.id}, user_id={self.user_id}, tag_id={self.tag_id})>"


class ProjectTag(Base):
    """Project-Tag association model"""

    __tablename__ = "project_tags"

    id = Column(UUID(as_uuid=True), primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )

    project = relationship("Project", backref="project_tags")
    tag = relationship("Tag", backref="project_tags")

    __table_args__ = (
        UniqueConstraint("project_id", "tag_id", name="unique_project_tag"),
    )

    def __repr__(self):
        return f"<ProjectTag(id={self.id}, project_id={self.project_id}, tag_id={self.tag_id})>"
