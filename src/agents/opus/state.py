from langgraph.graph import MessagesState


# TypedDict
class AgentState(MessagesState):
    next: str
