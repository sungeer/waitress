from pydantic import BaseModel


class TaskSubmitSchema(BaseModel):
    name: str  # 任务名,透传给后台任务,便于区分


class TaskStatusSchema(BaseModel):
    task_id: str
