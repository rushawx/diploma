from typing import List

import numpy as np

from app.auth.auth import get_current_active_user
from app.db.engine import User, Tag, UserTag
from app.models.users import UserResponse
from app.utils.utils import get_db
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/avatars", tags=["avatars"])


def compile_user_tags_vector(user_id: str, db, all_tags: List[Tag]) -> np.ndarray:
    """Compile a tags vector for a user based on their tags"""
    user_tags = db.query(UserTag).filter(UserTag.user_id == user_id).all()

    tag_set = {ut.tag_id for ut in user_tags}

    tag_idx_dict = {tag.id: idx for idx, tag in enumerate(all_tags)}

    vector = np.zeros(len(all_tags), dtype=np.int32)
    for tag_id in tag_set:
        if tag_id in tag_idx_dict:
            vector[tag_idx_dict[tag_id]] = 1

    return vector


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors"""
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))


@router.get("/my", response_model=UserResponse)
async def get_my_avatar(
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Get current user's associated avatar"""
    if not current_user.avatar_id:
        raise HTTPException(status_code=404, detail="No avatar associated")

    avatar = db.query(User).filter(User.id == current_user.avatar_id).first()
    if not avatar:
        raise HTTPException(status_code=404, detail="Associated avatar not found")

    return UserResponse(
        id=str(avatar.id),
        nick_name=avatar.nick_name,
        first_name=avatar.first_name,
        middle_name=avatar.middle_name,
        last_name=avatar.last_name,
        email_address=avatar.email_address,
        phone_number=avatar.phone_number,
        self_bio=avatar.self_bio,
        user_type=avatar.user_type,
        password=avatar.password,
        avatar_id=str(avatar.avatar_id) if avatar.avatar_id else None,
        created_at=avatar.created_at.isoformat() if avatar.created_at else None,
        updated_at=avatar.updated_at.isoformat() if avatar.updated_at else None,
        deleted_at=avatar.deleted_at.isoformat() if avatar.deleted_at else None,
        modified_by=str(avatar.modified_by) if avatar.modified_by else None,
    )


@router.get("/recommend", response_model=List[UserResponse])
async def recommend_avatar(
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Recommend avatars based on user's tags similarity"""
    all_tags = db.query(Tag).all()
    if not all_tags:
        raise HTTPException(status_code=404, detail="No tags available")

    user_vector = compile_user_tags_vector(str(current_user.id), db, all_tags)

    avatars = db.query(User).filter(User.user_type == "avatar").all()

    if not avatars:
        raise HTTPException(status_code=404, detail="No avatars available")

    avatar_scores = []
    for avatar in avatars:
        avatar_vector = compile_user_tags_vector(str(avatar.id), db, all_tags)
        similarity = cosine_similarity(user_vector, avatar_vector)
        avatar_scores.append((avatar, similarity))

    avatar_scores.sort(key=lambda x: x[1], reverse=True)

    return [
        UserResponse(
            id=str(avatar.id),
            nick_name=avatar.nick_name,
            first_name=avatar.first_name,
            middle_name=avatar.middle_name,
            last_name=avatar.last_name,
            email_address=avatar.email_address,
            phone_number=avatar.phone_number,
            self_bio=avatar.self_bio,
            user_type=avatar.user_type,
            password=avatar.password,
            avatar_id=str(avatar.avatar_id) if avatar.avatar_id else None,
            created_at=avatar.created_at.isoformat() if avatar.created_at else None,
            updated_at=avatar.updated_at.isoformat() if avatar.updated_at else None,
            deleted_at=avatar.deleted_at.isoformat() if avatar.deleted_at else None,
            modified_by=str(avatar.modified_by) if avatar.modified_by else None,
        )
        for avatar, _ in avatar_scores[:10]
    ]


@router.get("/", response_model=List[UserResponse])
async def get_avatars(
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Get all avatars"""
    avatars = db.query(User).filter(User.user_type == "avatar").all()
    return [
        UserResponse(
            id=str(avatar.id),
            nick_name=avatar.nick_name,
            first_name=avatar.first_name,
            middle_name=avatar.middle_name,
            last_name=avatar.last_name,
            email_address=avatar.email_address,
            phone_number=avatar.phone_number,
            self_bio=avatar.self_bio,
            user_type=avatar.user_type,
            password=avatar.password,
            avatar_id=str(avatar.avatar_id) if avatar.avatar_id else None,
            created_at=avatar.created_at.isoformat() if avatar.created_at else None,
            updated_at=avatar.updated_at.isoformat() if avatar.updated_at else None,
            deleted_at=avatar.deleted_at.isoformat() if avatar.deleted_at else None,
            modified_by=str(avatar.modified_by) if avatar.modified_by else None,
        )
        for avatar in avatars
    ]


@router.get("/{avatar_id}", response_model=UserResponse)
async def get_avatar(
    avatar_id: str,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Get a specific avatar"""
    avatar = db.query(User).filter(User.id == avatar_id, User.user_type == "avatar").first()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    return UserResponse(
        id=str(avatar.id),
        nick_name=avatar.nick_name,
        first_name=avatar.first_name,
        middle_name=avatar.middle_name,
        last_name=avatar.last_name,
        email_address=avatar.email_address,
        phone_number=avatar.phone_number,
        self_bio=avatar.self_bio,
        user_type=avatar.user_type,
        password=avatar.password,
        avatar_id=str(avatar.avatar_id) if avatar.avatar_id else None,
        created_at=avatar.created_at.isoformat() if avatar.created_at else None,
        updated_at=avatar.updated_at.isoformat() if avatar.updated_at else None,
        deleted_at=avatar.deleted_at.isoformat() if avatar.deleted_at else None,
        modified_by=str(avatar.modified_by) if avatar.modified_by else None,
    )


@router.put("/select/{avatar_id}")
async def select_avatar(
    avatar_id: str,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Associate current user with an avatar"""
    avatar = db.query(User).filter(User.id == avatar_id, User.user_type == "avatar").first()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")

    current_user.avatar_id = avatar.id
    db.commit()

    return {
        "message": f"Successfully associated with avatar: {avatar.nick_name}",
        "avatar_id": str(avatar.id),
        "avatar_name": avatar.nick_name,
    }
