import os
import uuid
import threading
import queue
from dataclasses import dataclass, field
from typing import Optional, Generator

from src.graphs.main_graph import build_graph
from src.utils.generate_uuid import get_unique_id
from src.utils.logger import get_logger
from src.prompt.critique_prompt import create_cirtique_prompt
from src.prompt.summarizer_prompt import create_summary_prompt
from src.prompt.synthesiser_prompt import create_synthesiser_prompt
from src.config.settings import SAVE_PROMPT_TO


# ─── Data Models ────────────────────────────────────────────────────────────────

@dataclass
class ChatMessage:
    role: str          # "user" | "assistant"
    content: str
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    iterations: Optional[int] = None
    draft_count: Optional[int] = None


@dataclass
class SessionState:
    session_id: str
    messages: list[ChatMessage] = field(default_factory=list)
    workflow: object = None          # compiled LangGraph
    config: dict = field(default_factory=dict)
    is_initialized: bool = False


# ─── Backend Class ───────────────────────────────────────────────────────────────

class ResearchBackend:
    """
    Manages one LangGraph workflow session per Streamlit session.
    All heavy initialisation is done once and cached.
    """
    
    def __init__(self):
        self.logger = get_logger()

        print("DEBUG: Backend init start")

        try:
            print("DEBUG: prewarm start")
            self.prewarm()
            print("DEBUG: prewarm done")

            print("DEBUG: ensure_prompts start")
            self.ensure_prompts()
            print("DEBUG: ensure_prompts done")

            print("DEBUG: build_graph start")
            self.workflow = build_graph()
            print("DEBUG: build_graph done")

            print("DEBUG: Backend init success")

        except Exception as e:
            print("DEBUG: Backend init failed")
            import traceback
            traceback.print_exc()
            raise

    # ── One-time warm-up (call on app boot or first use) ──────────────────────

    @staticmethod
    def prewarm():
        """Load ChromaDB, embedding model and Groq LLM into their lru_caches."""
        from src.rag.retriever import get_vector_store
        from src.model.chat_model import llm_model
        get_vector_store()
        llm_model()

    # ── Prompt file bootstrap ─────────────────────────────────────────────────

    @staticmethod
    def ensure_prompts():
        """Create prompt JSON files if they don't exist yet."""
        os.makedirs(SAVE_PROMPT_TO, exist_ok=True)

        files = os.listdir(SAVE_PROMPT_TO)

        if "critique_prompt.json" not in files:
            create_cirtique_prompt(name=f"{SAVE_PROMPT_TO}/critique_prompt.json")

        if "synthesiser_prompt.json" not in files:
            create_synthesiser_prompt(name=f"{SAVE_PROMPT_TO}/synthesiser_prompt.json")

        if "summary_prompt.json" not in files:
            create_summary_prompt(name=f"{SAVE_PROMPT_TO}/summary_prompt.json")

    # ── Session factory ───────────────────────────────────────────────────────

    def create_session(self) -> SessionState:
        """Return a brand-new SessionState with its own graph + config."""
        session_id = get_unique_id()
        config = {
            "configurable": {"thread_id": session_id},
            "metadata":     {"thread_id": session_id},
            "run_name":     "agentic-workflow-streamlit",
        }
        workflow = build_graph()

        return SessionState(
            session_id=session_id,
            workflow=workflow,
            config=config,
            is_initialized=True,
        )

    # ── Streaming query ───────────────────────────────────────────────────────

    def stream_response(
        self,
        session: SessionState,
        query: str,
        max_iterations: int = 5,
    ) -> Generator[str, None, None]:
        """
        Stream assistant tokens for *query* and yield them one by one.
        After the stream ends, attach metadata (iterations, draft count)
        to the last assistant message stored in session.messages.
        """
        initial_state = {
            "query": query,
            "max_iterations": max_iterations,
            "iterations": 0,
        }

        full_response = []

        for message_chunk, _metadata in session.workflow.stream(
            initial_state,
            config=session.config,
            stream_mode="messages",
        ):
            if message_chunk.content:
                token = message_chunk.content
                full_response.append(token)
                yield token

        # ── Post-stream: harvest final state metadata ────────────────────────
        try:
            final_state = session.workflow.get_state(session.config).values
            iterations  = final_state.get("iterations", None)
            drafts      = final_state.get("draft_answer", [])
            draft_count = len(drafts)
        except Exception:
            iterations  = None
            draft_count = None

        # Store the complete assistant message
        assistant_msg = ChatMessage(
            role="assistant",
            content="".join(full_response),
            iterations=iterations,
            draft_count=draft_count,
        )
        session.messages.append(assistant_msg)

    # ── Convenience: add user message ────────────────────────────────────────

    @staticmethod
    def add_user_message(session: SessionState, content: str) -> ChatMessage:
        msg = ChatMessage(role="user", content=content)
        session.messages.append(msg)
        return msg

    # ── Health-check / diagnostics ────────────────────────────────────────────

    @staticmethod
    def list_available_prompts() -> list[str]:
        if not os.path.exists(SAVE_PROMPT_TO):
            return []
        return os.listdir(SAVE_PROMPT_TO)