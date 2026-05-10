import operator
from typing import TypedDict, Annotated


class AgentState(TypedDict):
    query: str
    retrieved_docs: Annotated[list[str], operator.add]
    draft_answer: Annotated[list[str], operator.add]
    critique: str
    critique_score: float
    final_answer: str
    iterations: int
    max_iterations: int