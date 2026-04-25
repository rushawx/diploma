from app.auth.auth import get_current_active_user
from app.db.engine import User
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def get_users(current_user: User = Depends(get_current_active_user)):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{user_id}")
async def get_user(user_id: str, current_user: User = Depends(get_current_active_user)):
    raise NotImplementedError("This endpoint is not implemented yet.")


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
