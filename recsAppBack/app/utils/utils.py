import uuid

from app.config import settings
from app.db.engine import User, session
from sqlalchemy.orm import Session
from sqlalchemy.sql import text


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


def init_superuser(db: Session = next(get_db())):
    db.execute(text(f"DELETE FROM users WHERE nick_name = '{settings.ADMIN_USERNAME}'"))
    db.commit()
    superuser = User(
        id=uuid.uuid4(),
        nick_name=settings.ADMIN_USERNAME,
        password=settings.ADMIN_PASSWORD,
    )
    db.add(superuser)
    db.commit()
    db.refresh(superuser)
    return superuser
