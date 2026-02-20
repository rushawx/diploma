from fastapi import APIRouter

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{user_id}")
async def get_recommendations_by_user(user_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")
