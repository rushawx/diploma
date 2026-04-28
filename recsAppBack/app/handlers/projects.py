import uuid
from typing import List

from app.auth.auth import get_current_active_user
from app.db.engine import Project, User, session
from app.models.projects import ProjectCreate, ProjectListResponse, ProjectResponse, ProjectUpdate, ProjectWithEmbedding
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectListResponse])
async def get_projects(current_user: User = Depends(get_current_active_user)):
    """Get all projects"""
    db = session()
    try:
        projects = db.query(Project).filter(Project.deleted_at.is_(None)).all()
        return projects
    finally:
        db.close()


@router.get("/with-embeddings", response_model=List[ProjectWithEmbedding])
async def get_projects_with_embeddings(current_user: User = Depends(get_current_active_user)):
    """Get all projects with embeddings for similarity search"""
    db = session()
    try:
        projects = db.query(Project).filter(
            Project.deleted_at.is_(None),
            Project.embedding.isnot(None)
        ).all()
        return projects
    finally:
        db.close()


@router.get("/user/{user_id}", response_model=List[ProjectListResponse])
async def get_projects_by_user(
    user_id: str, current_user: User = Depends(get_current_active_user)
):
    """Get all projects for a specific user"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    db = session()
    try:
        projects = db.query(Project).filter(
            Project.modified_by == user_uuid,
            Project.deleted_at.is_(None)
        ).all()
        return projects
    finally:
        db.close()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str, current_user: User = Depends(get_current_active_user)
):
    """Get a specific project by ID"""
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )

    db = session()
    try:
        project = db.query(Project).filter(
            Project.id == project_uuid,
            Project.deleted_at.is_(None)
        ).first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        return project
    finally:
        db.close()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new project"""
    db = session()
    try:
        new_project = Project(
            id=uuid.uuid4(),
            title_rus=project_data.title_rus,
            title_eng=project_data.title_eng,
            annotation=project_data.annotation,
            description=project_data.description,
            embedding=project_data.embedding,
            modified_by=current_user.id
        )

        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        return new_project
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )
    finally:
        db.close()


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update an existing project"""
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )

    db = session()
    try:
        project = db.query(Project).filter(
            Project.id == project_uuid,
            Project.deleted_at.is_(None)
        ).first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        project.modified_by = current_user.id

        db.commit()
        db.refresh(project)

        return project
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )
    finally:
        db.close()


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Soft delete a project"""
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )

    db = session()
    try:
        project = db.query(Project).filter(
            Project.id == project_uuid,
            Project.deleted_at.is_(None)
        ).first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        from datetime import datetime
        project.deleted_at = datetime.now()
        project.modified_by = current_user.id

        db.commit()

        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )
    finally:
        db.close()
