from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Any
import uuid


class ProjectBase(BaseModel):
    title_rus: str = Field(..., max_length=512)
    title_eng: Optional[str] = Field(None, max_length=512)
    annotation: Optional[str] = None
    description: Optional[str] = None
    embedding: Optional[List[float]] = None

    @field_validator('embedding', mode='before')
    @classmethod
    def parse_embedding(cls, v: Any) -> Optional[List[float]]:
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if hasattr(v, 'tolist'):
            return v.tolist()
        return list(v)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title_rus: Optional[str] = Field(None, max_length=512)
    title_eng: Optional[str] = Field(None, max_length=512)
    annotation: Optional[str] = None
    description: Optional[str] = None
    chosen_by: Optional[uuid.UUID] = None


class ProjectResponse(ProjectBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    modified_by: Optional[uuid.UUID] = None
    chosen_by: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Simplified response model for project listings"""
    id: uuid.UUID
    title_rus: str
    title_eng: Optional[str] = None
    annotation: Optional[str] = None
    description: Optional[str] = None
    chosen_by: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


class ProjectWithEmbedding(BaseModel):
    """Project model with embedding for similarity search"""
    id: uuid.UUID
    title_rus: str
    title_eng: Optional[str] = None
    annotation: Optional[str] = None
    description: Optional[str] = None
    embedding: List[float]

    class Config:
        from_attributes = True


class ProjectWithTags(BaseModel):
    """Project model with tags vector for tag-based similarity search"""
    id: uuid.UUID
    title_rus: str
    title_eng: Optional[str] = None
    annotation: Optional[str] = None
    description: Optional[str] = None
    tags: List[float]

    class Config:
        from_attributes = True