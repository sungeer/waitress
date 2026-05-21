from pydantic import BaseModel


class TokenRequest(BaseModel):
    user_id: int  # 对应 users.ref_id
    username: str
    display_name: str | None = None
    email: str | None = None
