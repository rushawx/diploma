import uuid

import numpy as np

from app.config import settings
from app.db.engine import User, session, Tag
from app.models.profile import UserResponse
from app.models.tags import TagBase
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


def user_to_response(user: User) -> UserResponse:
    """Convert a User SQLAlchemy model to UserResponse."""
    return UserResponse(
        id=str(user.id),
        nick_name=user.nick_name,
        first_name=user.first_name,
        middle_name=user.middle_name,
        last_name=user.last_name,
        email_address=user.email_address,
        phone_number=user.phone_number,
        self_bio=user.self_bio,
        user_type=user.user_type,
        password=user.password,
        avatar_id=str(user.avatar_id) if user.avatar_id else None,
        created_at=user.created_at.isoformat() if user.created_at else None,
        updated_at=user.updated_at.isoformat() if user.updated_at else None,
        deleted_at=user.deleted_at.isoformat() if user.deleted_at else None,
        modified_by=str(user.modified_by) if user.modified_by else None,
    )


def tag_to_response(tag: Tag) -> TagBase:
    """Convert a Tag SQLAlchemy model to TagBase."""
    return TagBase(
        id=str(tag.id),
        name=tag.name,
        created_at=tag.created_at.isoformat() if tag.created_at else None,
        updated_at=tag.updated_at.isoformat() if tag.updated_at else None,
    )


def cosine_similarity(vec1: np.ndarray | list, vec2: np.ndarray | list) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector (list or numpy array)
        vec2: Second vector (list or numpy array)

    Returns:
        Cosine similarity score between 0 and 1
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(np.dot(vec1, vec2) / (norm1 * norm2))
