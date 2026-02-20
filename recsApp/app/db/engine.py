import datetime
import os

import sqlalchemy as sa
from dotenv import load_dotenv
from sqlalchemy import UUID, Column, DateTime, String
from sqlalchemy.orm import sessionmaker

load_dotenv()

POSTGRES_USER = os.getenv("PG_USER")
POSTGRES_PASSWORD = os.getenv("PG_PASSWORD")
POSTGRES_HOST = os.getenv("PG_HOST")
POSTGRES_PORT = os.getenv("PG_PORT")
POSTGRES_DB = os.getenv("PG_DATABASE")
DB_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = sa.create_engine(DB_URL)

session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

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
