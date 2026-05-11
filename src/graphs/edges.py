from langgraph.graph import StateGraph, START, END
from typing import Literal
from src.graphs.nodes import summary, critique, synthesiser, retriever
from src.graphs.state import AgentState


def perform_evaluation(state: AgentState) -> Literal['approved', 'not_approved']:
    return 'approved' if (
        (state['critique_score'] >= 6) or (state['iterations'] >= state['max_iterations'])
    ) else 'not_approved'


def build_edges(graph):
    graph.add_edge(START, 'retriever')
    graph.add_edge('retriever', 'summary')
    graph.add_edge('summary', 'critique')
    graph.add_conditional_edges('critique', perform_evaluation, 
                               {
                                   'approved': 'final_answer',
                                   'not_approved': 'synthesiser'
                               })
    graph.add_edge('synthesiser', 'critique')
    graph.add_edge('final_answer', END)