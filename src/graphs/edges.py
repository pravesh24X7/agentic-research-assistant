from langgraph.graph import StateGraph, START, END
from src.graphs.nodes import summary, critique, synthesiser, retriever


def build_edges(graph):
    graph.add_edge(START, 'retriever')
    graph.add_edge('retriever', 'summary')
    graph.add_edge('summary', 'critique')
    graph.add_edge('critique', 'synthesiser')
    graph.add_edge('synthesiser', END)