from pydantic import BaseModel, Field


class LoginInSchema(BaseModel):
    username: str
    password: str


class LoginOutSchema(BaseModel):
    token: str
    user_id: int
    username: str
    display_name: str
