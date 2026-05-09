from pydantic import BaseModel


class UserLogin(BaseModel):
    nick_name: str
    password: str


class UserSignup(BaseModel):
    nick_name: str
    password: str
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    email_address: str | None = None
    phone_number: str | None = None
    self_bio: str | None = None
    user_type: str = "student"


class UserResponse(BaseModel):
    id: str
    nick_name: str
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    email_address: str | None = None
    phone_number: str | None = None
    self_bio: str | None = None
    user_type: str = "student"
    password: str
    avatar_id: str | None = None
    created_at: str
    updated_at: str
    deleted_at: str | None = None
    modified_by: str | None = None
