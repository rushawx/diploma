from fastapi import APIRouter

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.get("/")
async def get_interactions():
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{user_id}")
async def get_interactions_by_user(user_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{interaction_id}")
async def get_interaction(interaction_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.post("/")
async def create_interaction():
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.put("/{interaction_id}")
async def update_interaction(interaction_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.delete("/{interaction_id}")
async def delete_interaction(interaction_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")
