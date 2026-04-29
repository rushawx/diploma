from pydantic import BaseModel


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


class UserLogin(BaseModel):

    nick_name: str
    password: str
