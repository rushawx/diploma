import datetime

import sqlalchemy as sa
from app.config import settings
from sqlalchemy import UUID, Column, DateTime, String
from sqlalchemy.orm import sessionmaker

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
    embedding = Column(String, unique=False)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    deleted_at = Column(DateTime, nullable=True)
    modified_by = Column(String, nullable=True)
