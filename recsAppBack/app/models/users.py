from pydantic import BaseModel


class User(BaseModel):

    id: str
    nick_name: str
    # first_name: str
    # middle_name: str
    # last_name: str
    # email_address: str
    # phone_number: str
    # self_bio: str
    # user_type: str
    # embedding: str
    password: str
    # created_at: str
    # updated_at: str
    # deleted_at: str | None = None
    # modified_by: str | None = None
