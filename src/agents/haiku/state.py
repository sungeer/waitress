from langgraph.graph import MessagesState


class AgentState(MessagesState):
    tool_rounds: int
