import os
import uuid

from app.db.engine import User, session
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

load_dotenv()


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


def init_superuser(db: Session = next(get_db())):
    db.execute(text("DELETE FROM users WHERE nick_name = 'SYSTEM'"))
    db.commit()
    superuser = User(
        id=uuid.uuid4(), nick_name="SYSTEM", password=os.getenv("ADMIN_PASSWORD")
    )
    db.add(superuser)
    db.commit()
    db.refresh(superuser)
    return superuser
