from pydantic import BaseModel


class UserSignup(BaseModel):

    nick_name: str
    password: str

class UserLogin(BaseModel):

    nick_name: str
    password: str
