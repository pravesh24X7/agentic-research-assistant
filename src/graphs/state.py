import operator
from typing import TypedDict, Annotated


class AgentState(TypedDict):
    query: str
    retrieved_docs: Annotated[list[str], operator.add]
    draft_answer: str
    critique: str
    critique_score: float
    final_answer: str
    interations: int