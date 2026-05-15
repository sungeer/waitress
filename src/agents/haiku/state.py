from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """继承 MessagesState，自带 messages 字段和 add_messages reducer"""
    next: str
    tool_rounds: int
