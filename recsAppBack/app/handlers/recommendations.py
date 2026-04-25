from app.auth.auth import get_current_active_user
from app.db.engine import User
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{user_id}")
async def get_recommendations_by_user(
    user_id: str, current_user: User = Depends(get_current_active_user)
):
    raise NotImplementedError("This endpoint is not implemented yet.")
