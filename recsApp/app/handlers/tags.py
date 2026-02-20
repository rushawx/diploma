from fastapi import APIRouter

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/")
async def get_tags():
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{user_id}")
async def get_tags_for_user(user_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{tag_id}")
async def get_tag(tag_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.post("/")
async def create_tag():
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.put("/{tag_id}")
async def update_tag(tag_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")
