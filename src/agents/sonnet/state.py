from pydantic import BaseModel, Field
from langgraph.graph import MessagesState


class AgentState(MessagesState):
    next: str
    order_id: str    # 目标订单ID
    amount: float    # 订单金额


class IntentResult(BaseModel):
    """意图分类结果"""
    next: str = Field(description='cancel_order 或 query_order')


class OrderDecision(BaseModel):
    """订单取消决策"""
    next: str = Field(description='下一步操作: approval 或 cancel')
    order_id: str = Field(description='订单编号，如 ORD-2847')
    amount: float = Field(description='订单金额')
