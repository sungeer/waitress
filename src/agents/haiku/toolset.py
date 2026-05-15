from pydantic import BaseModel, Field
from langchain_core.tools import tool


class NotificationInput(BaseModel):
    message: str = Field(description='要发送的通知内容')
    recipient: str = Field(description='接收人')


@tool(args_schema=NotificationInput)
def send_notification(message: str, recipient: str) -> str:
    """向指定接收人发送通知消息（模拟）"""
    return f'已向 [{recipient}] 发送通知：{message}'
