from langgraph.graph import MessagesState


class AgentState(MessagesState):
    next: str
    intent: str  # 原始意图: cancel_order / query_order
    order_id: str  # 目标订单ID
    amount: float  # 订单金额
