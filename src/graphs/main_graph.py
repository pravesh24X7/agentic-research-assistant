import sqlite3

from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver

from src.graphs.state import AgentState
from src.graphs.edges import build_edges
from src.graphs.nodes import retriever, summary, critique, synthesiser
from src.config.settings import DB_NAME



def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node('retriever', retriever)
    graph.add_node('summary', summary)
    graph.add_node('critique', critique)
    graph.add_node('synthesiser', synthesiser)

    build_edges(graph=graph)

    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    checkpointer = SqliteSaver(conn=conn)

    return graph.compile(checkpointer=checkpointer)