from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def get_users():
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{user_id}")
async def get_user(user_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.post("/")
async def create_user():
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.put("/{user_id}")
async def update_user(user_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")
