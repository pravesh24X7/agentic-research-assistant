import os
import uuid
from dataclasses import dataclass, field
from typing import Optional, Generator, Tuple, List

from src.graphs.main_graph import build_graph
from src.utils.generate_uuid import get_unique_id
from src.utils.logger import get_logger
from src.prompt.critique_prompt import create_cirtique_prompt
from src.prompt.summarizer_prompt import create_summary_prompt
from src.prompt.synthesiser_prompt import create_synthesiser_prompt
from src.config.settings import SAVE_PROMPT_TO


# ─── Node → human-readable status label ──────────────────────────────────────
NODE_STATUS = {
    "retriever":     "📚 Retrieving documents...",
    "search_online": "🔍 Searching the web...",
    "summary":       "✍️  Drafting initial answer...",
    "critique":      "🧠 Critiquing draft...",
    "synthesiser":   "🔄 Refining answer...",
    "final_answer":  "✅ Preparing final answer...",
}


# ─── Data Models ─────────────────────────────────────────────────────────────

@dataclass
class ChatMessage:
    role: str
    content: str
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    iterations: Optional[int] = None
    draft_count: Optional[int] = None


@dataclass
class SessionState:
    session_id: str
    topic: str = "New Chat"
    messages: list = field(default_factory=list)
    workflow: object = None
    config: dict = field(default_factory=dict)
    is_initialized: bool = False
    # Tracks which file paths have already been ingested for this session
    ingested_files: list = field(default_factory=list)


# ─── Backend ─────────────────────────────────────────────────────────────────

class ResearchBackend:

    def __init__(self):
        self.logger = get_logger()
        print("DEBUG: Backend init start")
        try:
            self.prewarm()
            self.ensure_prompts()
            self.workflow = build_graph()
            print("DEBUG: Backend init success")
        except Exception:
            import traceback
            traceback.print_exc()
            raise

    # ── Boot helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def prewarm():
        from src.rag.retriever import get_vector_store
        from src.model.chat_model import llm_model
        get_vector_store()
        llm_model()

    @staticmethod
    def ensure_prompts():
        os.makedirs(SAVE_PROMPT_TO, exist_ok=True)
        files = os.listdir(SAVE_PROMPT_TO)
        if "critique_prompt.json" not in files:
            create_cirtique_prompt(name=f"{SAVE_PROMPT_TO}/critique_prompt.json")
        if "synthesiser_prompt.json" not in files:
            create_synthesiser_prompt(name=f"{SAVE_PROMPT_TO}/synthesiser_prompt.json")
        if "summary_prompt.json" not in files:
            create_summary_prompt(name=f"{SAVE_PROMPT_TO}/summary_prompt.json")

    # ── Session factory ───────────────────────────────────────────────────────

    def create_session(self, topic: str = "New Chat") -> SessionState:
        session_id = get_unique_id()
        config = {
            "configurable": {"thread_id": session_id},
            "metadata":     {"thread_id": session_id},
            "run_name":     "agentic-workflow-streamlit",
        }
        return SessionState(
            session_id=session_id,
            topic=topic,
            workflow=build_graph(),
            config=config,
            is_initialized=True,
        )

    # ── Document ingestion ────────────────────────────────────────────────────

    def ingest_documents(self, file_paths: List[str]) -> None:
        """
        Load documents from *file_paths* into the vector store.

        Supports PDF, TXT, MD, DOCX, CSV, JSON, and HTML files via
        LangChain community document loaders.  Only files not yet
        indexed (tracked per session via SessionState.ingested_files)
        should be passed in – the caller (frontend) is responsible for
        deduplication; this method ingests everything it receives.

        Raises on loader / vector-store errors so the caller can surface
        a user-friendly message.
        """
        from src.rag.retriever import get_vector_store

        docs = []
        for path in file_paths:
            ext = os.path.splitext(path)[-1].lower()
            try:
                if ext == ".pdf":
                    from langchain_community.document_loaders import PyPDFLoader
                    loader = PyPDFLoader(path)
                elif ext in (".txt", ".md"):
                    from langchain_community.document_loaders import TextLoader
                    loader = TextLoader(path, encoding="utf-8")
                elif ext == ".docx":
                    from langchain_community.document_loaders import Docx2txtLoader
                    loader = Docx2txtLoader(path)
                elif ext == ".csv":
                    from langchain_community.document_loaders import CSVLoader
                    loader = CSVLoader(path)
                elif ext == ".json":
                    from langchain_community.document_loaders import JSONLoader
                    # Assumes the JSON is an array of objects with a "text" key;
                    # adjust jq_schema to match your data format.
                    loader = JSONLoader(path, jq_schema=".[]", text_content=False)
                elif ext in (".html", ".htm"):
                    from langchain_community.document_loaders import UnstructuredHTMLLoader
                    loader = UnstructuredHTMLLoader(path)
                else:
                    self.logger.warning(f"Unsupported file type skipped: {path}")
                    continue

                loaded = loader.load()
                # Tag each document chunk with the source file name
                for doc in loaded:
                    doc.metadata.setdefault("source", os.path.basename(path))
                docs.extend(loaded)
                self.logger.info(f"Loaded {len(loaded)} chunk(s) from {path}")

            except Exception as e:
                self.logger.error(f"Failed to load {path}: {e}")
                raise RuntimeError(f"Could not load '{os.path.basename(path)}': {e}") from e

        if not docs:
            self.logger.info("No documents to ingest.")
            return

        # Split long documents into overlapping chunks for better retrieval
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=150,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            split_docs = splitter.split_documents(docs)
            self.logger.info(f"Split into {len(split_docs)} chunks total.")
        except Exception as e:
            self.logger.warning(f"Text splitting failed ({e}); using raw docs.")
            split_docs = docs

        # Add to the shared vector store
        vs = get_vector_store()
        vs.add_documents(split_docs)
        self.logger.info(f"Ingested {len(split_docs)} chunks into vector store.")

    # ── Streaming ─────────────────────────────────────────────────────────────

    def stream_response(
        self,
        session: SessionState,
        query: str,
        max_iterations: int = 5,
        use_web_search: bool = False,
        uploaded_files: Optional[List[str]] = None,
    ) -> Generator[Tuple[Optional[str], Optional[str]], None, None]:
        """
        Yields (token, status) tuples:
          (None,  "📚 Retrieving...")  → stage label shown as live pill
          ("text", None)               → final answer text shown once at the end

        uploaded_files: list of absolute file paths that have been saved to
        disk and ingested into the vector store.  They are forwarded to the
        graph state so nodes (e.g. retriever) can filter by source if needed.
        """
        uploaded_files = uploaded_files or []

        initial_state = {
            "query":          query,
            "max_iterations": max_iterations,
            "iterations":     0,
            "use_web_search": use_web_search,
            "search_results": "",
            "uploaded_files": uploaded_files,
            "thread_id":      session.session_id,
            "context":        "",
            "citations":      "",
        }

        # Phase 1 — stream node-level updates; emit a status label per node
        seen_nodes: set = set()
        for update in session.workflow.stream(
            initial_state,
            config=session.config,
            stream_mode="updates",
        ):
            for node_name, node_data in update.items():
                if node_name not in NODE_STATUS or node_name in seen_nodes:
                    continue
                seen_nodes.add(node_name)

                if node_name == "critique":
                    score = node_data.get("critique_score")
                    label = (
                        f"🧠 Critique complete — score {score}/10"
                        if score is not None else NODE_STATUS[node_name]
                    )
                elif node_name == "synthesiser":
                    itr = node_data.get("iterations")
                    label = (
                        f"🔄 Refining answer (iteration {itr})..."
                        if itr is not None else NODE_STATUS[node_name]
                    )
                else:
                    label = NODE_STATUS[node_name]

                yield (None, label)

        # Phase 2 — read final answer from persisted checkpoint
        final_answer = ""
        iterations   = None
        draft_count  = 0
        try:
            final_state  = session.workflow.get_state(session.config).values
            final_answer = (
                final_state.get("final_answer")
                or (final_state.get("draft_answer") or [""])[-1]
            )
            iterations  = final_state.get("iterations")
            draft_count = len(final_state.get("draft_answer") or [])
        except Exception as e:
            print(f"get_state failed: {e}")

        if final_answer:
            yield (final_answer, None)

        session.messages.append(ChatMessage(
            role="assistant",
            content=final_answer,
            iterations=iterations,
            draft_count=draft_count,
        ))

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def add_user_message(session: SessionState, content: str) -> ChatMessage:
        msg = ChatMessage(role="user", content=content)
        session.messages.append(msg)
        return msg

    @staticmethod
    def list_available_prompts() -> list:
        if not os.path.exists(SAVE_PROMPT_TO):
            return []
        return os.listdir(SAVE_PROMPT_TO)