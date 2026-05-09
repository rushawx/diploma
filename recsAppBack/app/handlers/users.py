from typing import Literal

from app.auth.auth import get_current_active_user
from app.db.engine import User
from app.models.users import UserResponse
from app.utils.utils import get_db, user_to_response
from fastapi import APIRouter, Depends, Query

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    user_type: Literal["student", "avatar"] | None = None,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Get all users, optionally filtered by user_type"""
    query = db.query(User)
    if user_type:
        query = query.filter(User.user_type == user_type)
    users = query.offset(skip).limit(limit).all()
    return [user_to_response(user) for user in users]


@router.get("/avatars")
async def get_avatars(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Get all avatar users"""
    users = (
        db.query(User)
        .filter(User.user_type == "avatar")
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [user_to_response(user) for user in users]


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Get a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="User not found")
    return user_to_response(user)


@router.post("/")
async def create_user(current_user: User = Depends(get_current_active_user)):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.put("/{user_id}")
async def update_user(
    user_id: str, current_user: User = Depends(get_current_active_user)
):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.delete("/{user_id}")
async def delete_user(
    user_id: str, current_user: User = Depends(get_current_active_user)
):
    raise NotImplementedError("This endpoint is not implemented yet.")
