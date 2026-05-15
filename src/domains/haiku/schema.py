from pydantic import BaseModel


class ThreadInSchema(BaseModel):
    content: str
    approver_id: str = ''


class ApprovalInSchema(BaseModel):
    thread_id: str
    operator: str = ''
