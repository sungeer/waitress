from langgraph.graph import MessagesState


class AgentState(MessagesState):
    next: str
    tool_rounds: int
