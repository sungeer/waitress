from pydantic import BaseModel


class CancelInSchema(BaseModel):
    content: str
    approver_id: str = ''


class ApprovalInSchema(BaseModel):
    thread_id: str
    operator: str = ''
    reason: str = ''
