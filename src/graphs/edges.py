from langgraph.graph import StateGraph, START, END
from typing import Literal
from src.graphs.nodes import summary, critique, synthesiser, retriever
from src.graphs.state import AgentState


def perform_evaluation(state: AgentState) -> Literal['approved', 'not_approved']:
    return 'approved' if (
        (state['critique_score'] >= 6) or (state['iterations'] >= state['max_iterations'])
    ) else 'not_approved'


def route_search(state: AgentState) -> Literal['search_online', 'summary']:
    if state.get('use_web_search', False):
        return 'search_online'
    return 'summary'


def build_edges(graph):
    graph.add_edge(START, 'retriever')
    graph.add_conditional_edges('retriever', route_search, {
        'search_online': 'search_online',
        'summary': 'summary'
    })
    graph.add_edge('search_online', 'summary')
    graph.add_edge('summary', 'critique')
    graph.add_conditional_edges('critique', perform_evaluation, 
                               {
                                   'approved': 'final_answer',
                                   'not_approved': 'synthesiser'
                               })
    graph.add_edge('synthesiser', 'critique')
    graph.add_edge('final_answer', END)