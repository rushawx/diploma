from app.auth.auth import get_current_active_user
from app.db.engine import User
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/")
async def get_projects(current_user: User = Depends(get_current_active_user)):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{user_id}")
async def get_projects_by_user(
    user_id: str, current_user: User = Depends(get_current_active_user)
):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.get("/{project_id}")
async def get_project(
    project_id: str, current_user: User = Depends(get_current_active_user)
):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.post("/")
async def create_project(current_user: User = Depends(get_current_active_user)):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.put("/{project_id}")
async def update_project(
    project_id: str, current_user: User = Depends(get_current_active_user)
):
    raise NotImplementedError("This endpoint is not implemented yet.")


@router.delete("/{project_id}")
async def delete_project(
    project_id: str, current_user: User = Depends(get_current_active_user)
):
    raise NotImplementedError("This endpoint is not implemented yet.")
