from fastapi import APIRouter

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/")
async def get_projects():
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{user_id}")
async def get_projects_by_user(user_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{project_id}")
async def get_project(project_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.post("/")
async def create_project():
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.put("/{project_id}")
async def update_project(project_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.delete("/{project_id}")
async def delete_project(project_id: int):
    raise NotImplementedError("This endpoint is not implemented yet.")
