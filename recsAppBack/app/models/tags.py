from typing import List
from pydantic import BaseModel


class TagBase(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str


class TagCreate(BaseModel):
    name: str


class UserTagCreate(BaseModel):
    user_id: str
    tag_id: str


class ProjectTagCreate(BaseModel):
    project_id: str
    tag_id: str


class UserTagResponse(BaseModel):
    id: str
    user_id: str
    tag_id: str
    created_at: str
    tag: TagBase | None = None


class ProjectTagResponse(BaseModel):
    id: str
    project_id: str
    tag_id: str
    created_at: str
    tag: TagBase | None = None


class TagNamesRequest(BaseModel):
    tag_names: List[str]