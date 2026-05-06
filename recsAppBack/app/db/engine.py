import datetime

import sqlalchemy as sa
from app.config import settings
from sqlalchemy import UUID, Column, DateTime, String, Text, ForeignKey, Float, Integer
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector

engine = sa.create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DB_ECHO,
)

session = sessionmaker(
    bind=engine, autocommit=settings.DB_AUTOCOMMIT, autoflush=settings.DB_AUTOFLUSH
)

Base = sa.orm.declarative_base()


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    user = relationship("User", backref="ratings")
    project = relationship("Project", backref="ratings")

    __table_args__ = (
        sa.UniqueConstraint("user_id", "project_id", name="unique_user_project_rating"),
    )


class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )


class UserTag(Base):
    __tablename__ = "user_tags"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    tag_id = Column(
        UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime, default=datetime.datetime.now)

    user = relationship("User", backref="user_tags")
    tag = relationship("Tag", backref="user_tags")

    __table_args__ = (sa.UniqueConstraint("user_id", "tag_id", name="unique_user_tag"),)


class ProjectTag(Base):
    __tablename__ = "project_tags"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    tag_id = Column(
        UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime, default=datetime.datetime.now)

    project = relationship("Project", backref="project_tags")
    tag = relationship("Tag", backref="project_tags")

    __table_args__ = (
        sa.UniqueConstraint("project_id", "tag_id", name="unique_project_tag"),
    )


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    nick_name = Column(String, unique=True)
    first_name = Column(String, unique=False)
    middle_name = Column(String, unique=False)
    last_name = Column(String, unique=False)
    email_address = Column(String, unique=True)
    phone_number = Column(String, unique=True)
    self_bio = Column(String, unique=False)
    user_type = Column(String, unique=False)
    password = Column(String)
    avatar_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    deleted_at = Column(DateTime, nullable=True)
    modified_by = Column(UUID(as_uuid=True), nullable=True)

    avatar = relationship("User", remote_side=[id], backref="avatar_users")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    title_rus = Column(String(512), nullable=False)
    title_eng = Column(String(512), nullable=True)
    annotation = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    embedding = Column(Vector(384), nullable=True)
    tags = Column(Vector(1861), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    deleted_at = Column(DateTime, nullable=True)
    modified_by = Column(UUID(as_uuid=True), nullable=True)
    chosen_by = Column(UUID(as_uuid=True), nullable=True)
