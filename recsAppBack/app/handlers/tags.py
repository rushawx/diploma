from app.auth.auth import get_current_active_user
from app.db.engine import User
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/")
async def get_tags(current_user: User = Depends(get_current_active_user)):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{user_id}")
async def get_tags_for_user(
    user_id: str, current_user: User = Depends(get_current_active_user)
):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{tag_id}")
async def get_tag(tag_id: str, current_user: User = Depends(get_current_active_user)):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.post("/")
async def create_tag(current_user: User = Depends(get_current_active_user)):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.put("/{tag_id}")
async def update_tag(
    tag_id: str, current_user: User = Depends(get_current_active_user)
):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: str, current_user: User = Depends(get_current_active_user)
):
    raise NotImplementedError("This endpoint is not implemented yet.")
