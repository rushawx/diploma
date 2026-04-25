from app.auth.auth import get_current_active_user
from app.db.engine import User
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.get("/")
async def get_interactions(current_user: User = Depends(get_current_active_user)):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{user_id}")
async def get_interactions_by_user(
    user_id: str, current_user: User = Depends(get_current_active_user)
):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{interaction_id}")
async def get_interaction(
    interaction_id: str, current_user: User = Depends(get_current_active_user)
):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.post("/")
async def create_interaction(current_user: User = Depends(get_current_active_user)):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.put("/{interaction_id}")
async def update_interaction(
    interaction_id: str, current_user: User = Depends(get_current_active_user)
):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.delete("/{interaction_id}")
async def delete_interaction(
    interaction_id: str, current_user: User = Depends(get_current_active_user)
):
    raise NotImplementedError("This endpoint is not implemented yet.")
