from pydantic import BaseModel


class SubmitRequest(BaseModel):
    task_id: str
