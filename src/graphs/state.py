import operator
from typing import TypedDict, Annotated


class AgentState(TypedDict):
    query: str
    retrieved_docs: list[str]
    search_results: str
    draft_answer: Annotated[list[str], operator.add]
    critique: str
    critique_score: float
    critique_score_history: Annotated[list[float], operator.add]
    final_answer: str
    iterations: int
    max_iterations: int
    use_web_search: bool
    uploaded_files: list[str]
    thread_id: str
    context: str
    citations: str