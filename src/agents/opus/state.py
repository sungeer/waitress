from typing import Literal

from pydantic import BaseModel, Field
from langgraph.graph import MessagesState


class AgentState(MessagesState):
    next: str


class IntentResult(BaseModel):
    """意图分类结果"""
    next: Literal['weather', 'time', 'news'] = Field(description='意图类型')
