from pydantic import BaseModel


class CustomInSchema(BaseModel):
    messages: str
    stream: bool = True
    message_id: str
    is_think: bool = False


class ApprovalInSchema(BaseModel):
    thread_id: str
    operator: str = ''
    reason: str = ''
