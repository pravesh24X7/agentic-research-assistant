import sqlite3
from functools import lru_cache

from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver

from src.graphs.state import AgentState
from src.graphs.edges import build_edges
from src.graphs.nodes import (
    retriever,
    summary,
    critique,
    synthesiser,
    generate_final_answer,
    search_online
)
from src.config.settings import DB_NAME


# -----------------------------------
# Shared SQLite Connection
# -----------------------------------
@lru_cache(maxsize=1)
def get_checkpointer():
    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )
    return SqliteSaver(conn=conn)


# -----------------------------------
# Shared Graph Build
# -----------------------------------
@lru_cache(maxsize=1)
def build_graph():

    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("retriever", retriever)
    graph.add_node("search_online", search_online)
    graph.add_node("summary", summary)
    graph.add_node("critique", critique)
    graph.add_node("synthesiser", synthesiser)
    graph.add_node("final_answer", generate_final_answer)

    # Edges
    build_edges(graph)

    # Single persistent checkpointer
    checkpointer = get_checkpointer()

    # Compile once
    compiled_graph = graph.compile(
        checkpointer=checkpointer
    )

    return compiled_graph