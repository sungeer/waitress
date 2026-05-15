from pydantic import BaseModel


class CustomInSchema(BaseModel):
    messages: list
    stream: bool = True
    message_id: str
    is_think: bool = False
    tool: str = ''
    agent: str = ''
