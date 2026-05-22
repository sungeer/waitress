from pydantic import BaseModel


class ChatInSchema(BaseModel):
    messages: str
    stream: bool = True
    message_id: str


class TaskStatusInSchema(BaseModel):
    task_id: str
