from typing import Literal, TypedDict

from pydantic import BaseModel


class CustomInSchema(BaseModel):
    messages: str
    stream: bool = True
    message_id: str
    is_think: bool = False


class IntentRoute(TypedDict):
    """LLM 意图分类的输出结构"""
    next: Literal['weather', 'time', 'news']
