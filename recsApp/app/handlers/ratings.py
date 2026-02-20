from fastapi import APIRouter

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.get("/")
async def get_ratings():
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{user_id}")
async def get_ratings_by_user(user_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{rating_id}")
async def get_rating(rating_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.post("/")
async def create_rating():
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.put("/{rating_id}")
async def update_rating(rating_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.delete("/{rating_id}")
async def delete_rating(rating_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")
