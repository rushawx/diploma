import uuid
from pydantic import BaseModel

from app.auth.auth import get_current_active_user
from app.db.engine import User, Tag, UserTag, ProjectTag
from app.models.tags import (
    TagBase,
    UserTagResponse,
    ProjectTagResponse,
    TagNamesRequest
)
from app.utils.utils import get_db
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=list[TagBase])
async def get_tags(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Get all tags"""
    tags = db.query(Tag).offset(skip).limit(limit).all()
    return [
        Tag(
            id=str(tag.id),
            name=tag.name,
            created_at=tag.created_at.isoformat() if tag.created_at else None,
            updated_at=tag.updated_at.isoformat() if tag.updated_at else None,
        )
        for tag in tags
    ]


@router.get("/{tag_id}", response_model=TagBase)
async def get_tag(
    tag_id: str,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Get a specific tag"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return Tag(
        id=str(tag.id),
        name=tag.name,
        created_at=tag.created_at.isoformat() if tag.created_at else None,
        updated_at=tag.updated_at.isoformat() if tag.updated_at else None,
    )


@router.get("/user/{user_id}", response_model=list[UserTagResponse])
async def get_user_tags(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Get all tags for a user"""
    user_tags = db.query(UserTag).filter(UserTag.user_id == user_id).all()
    results = []
    for user_tag in user_tags:
        tag = db.query(Tag).filter(Tag.id == user_tag.tag_id).first()
        tag_data = (
            Tag(
                id=str(tag.id),
                name=tag.name,
                created_at=tag.created_at.isoformat() if tag.created_at else None,
                updated_at=tag.updated_at.isoformat() if tag.updated_at else None,
            )
            if tag
            else None
        )
        results.append(
            UserTagResponse(
                id=str(user_tag.id),
                user_id=str(user_tag.user_id),
                tag_id=str(user_tag.tag_id),
                created_at=user_tag.created_at.isoformat() if user_tag.created_at else None,
                tag=tag_data,
            )
        )
    return results


@router.get("/project/{project_id}", response_model=list[ProjectTagResponse])
async def get_project_tags(
    project_id: str,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Get all tags for a project"""
    project_tags = db.query(ProjectTag).filter(ProjectTag.project_id == project_id).all()
    results = []
    for project_tag in project_tags:
        tag = db.query(Tag).filter(Tag.id == project_tag.tag_id).first()
        tag_data = (
            Tag(
                id=str(tag.id),
                name=tag.name,
                created_at=tag.created_at.isoformat() if tag.created_at else None,
                updated_at=tag.updated_at.isoformat() if tag.updated_at else None,
            )
            if tag
            else None
        )
        results.append(
            ProjectTagResponse(
                id=str(project_tag.id),
                project_id=str(project_tag.project_id),
                tag_id=str(project_tag.tag_id),
                created_at=project_tag.created_at.isoformat()
                if project_tag.created_at
                else None,
                tag=tag_data,
            )
        )
    return results


@router.post("/user/{user_id}")
async def add_user_tags(
    user_id: str,
    request: TagNamesRequest,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Add multiple tags to a user by tag names"""
    tag_names = request.tag_names
    if not tag_names:
        raise HTTPException(status_code=400, detail="At least one tag must be provided")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    added_count = 0
    skipped_count = 0

    for tag_name in tag_names:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            skipped_count += 1
            continue

        existing_user_tag = (
            db.query(UserTag)
            .filter(UserTag.user_id == user_id, UserTag.tag_id == tag.id)
            .first()
        )
        if existing_user_tag:
            skipped_count += 1
            continue

        new_user_tag = UserTag(id=uuid.uuid4(), user_id=user_id, tag_id=tag.id)
        db.add(new_user_tag)
        added_count += 1

    db.commit()

    return {
        "message": f"Added {added_count} tags to user, skipped {skipped_count} duplicates or invalid tags",
        "added_count": added_count,
        "skipped_count": skipped_count,
    }


@router.delete("/user/{user_id}")
async def delete_user_tags(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    """Delete all tags for a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    deleted_count = db.query(UserTag).filter(UserTag.user_id == user_id).delete()
    db.commit()

    return {
        "message": f"Deleted {deleted_count} tags for user",
        "deleted_count": deleted_count,
    }
