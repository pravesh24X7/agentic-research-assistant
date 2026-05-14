# frontend.py - Research Agent Streamlit UI
# Run: streamlit run frontend.py

import os
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

import traceback

print("DEBUG: frontend boot start")

try:
    import streamlit as st
    print("DEBUG: streamlit imported")
except Exception:
    print("DEBUG: streamlit import failed")
    traceback.print_exc()
    raise

try:
    from backend import ResearchBackend
    print("DEBUG: backend imported")
except Exception:
    print("DEBUG: backend import failed")
    traceback.print_exc()
    raise

st.set_page_config(
    page_title="Research Agent",
    page_icon="Research Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)

import time
from src.utils.bq_logger import log_to_bigquery


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=JetBrains+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');
    :root {
        --gold:#c9a84c; --gold-light:#e2c97e; --gold-dim:#8b6914;
        --bg-primary:#0d1117; --bg-secondary:#161b22; --bg-tertiary:#1c2333;
        --text-primary:#e6edf3; --text-secondary:#8b949e; --text-muted:#484f58;
        --border:#21262d; --border-gold:rgba(201,168,76,0.28); --radius:14px;
    }
    html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"] {
        background:var(--bg-primary) !important;
        font-family:'DM Sans',sans-serif; color:var(--text-primary);
    }
    #MainMenu,footer { visibility:hidden; }
    [data-testid="stSidebar"] {
        background:var(--bg-secondary) !important;
        border-right:1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] * {
        color:var(--text-primary) !important;
        font-family:'DM Sans',sans-serif !important;
    }
    [data-testid="stSidebar"] h1 {
        font-family:'Playfair Display',serif !important;
        color:var(--gold) !important;
        -webkit-text-fill-color:var(--gold) !important;
        font-size:1.25rem !important;
    }
    .stButton>button {
        width:100%;
        background:linear-gradient(135deg,var(--gold-dim),var(--gold)) !important;
        color:#0d1117 !important; font-weight:600 !important;
        border:none !important; border-radius:10px !important;
    }
    .stButton>button:hover { opacity:0.85 !important; }
    [data-testid="stChatMessage"] {
        background:var(--bg-secondary) !important;
        border:1px solid var(--border) !important;
        border-radius:var(--radius) !important;
        margin-bottom:0.75rem !important;
        animation:fadeUp 0.3s ease both;
    }
    @keyframes fadeUp {
        from { opacity:0; transform:translateY(8px); }
        to   { opacity:1; transform:translateY(0); }
    }
    [data-testid="stChatInput"] {
        background:var(--bg-secondary) !important;
        border:1px solid var(--border-gold) !important;
        border-radius:var(--radius) !important;
    }
    [data-testid="stChatInput"] textarea {
        background:transparent !important;
        color:var(--text-primary) !important;
        font-family:'DM Sans',sans-serif !important;
    }
    [data-testid="stChatInput"] textarea::placeholder { color:var(--text-muted) !important; }
    hr { border-color:var(--border) !important; margin:0.75rem 0 !important; }
    .stCaption { color:var(--text-muted) !important; font-size:0.72rem !important; }
    .main-header {
        text-align:center; padding:1.6rem 1rem 1rem;
        border-bottom:1px solid var(--border-gold); margin-bottom:1.5rem;
    }
    .main-header h1 {
        font-family:'Playfair Display',serif; font-size:2rem; font-weight:700;
        background:linear-gradient(135deg,#e2c97e 0%,#c9a84c 55%,#8b6914 100%);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        background-clip:text; margin:0;
    }
    .main-header p {
        color:var(--text-muted); font-size:0.78rem;
        text-transform:uppercase; letter-spacing:0.12em; margin:0.3rem 0 0;
    }
    .welcome-card {
        max-width:540px; margin:2.5rem auto; background:#1a2236;
        border:1px solid var(--border-gold); border-radius:18px;
        padding:2rem 1.8rem; text-align:center;
    }
    .welcome-card h2 {
        font-family:'Playfair Display',serif; color:var(--gold-light);
        font-size:1.4rem; margin:0.4rem 0 0.8rem;
    }
    .welcome-card p {
        color:var(--text-secondary) !important;
        font-size:0.88rem !important; line-height:1.7;
    }
    .meta-tag {
        display:inline-block; font-family:'JetBrains Mono',monospace;
        font-size:0.68rem; padding:2px 9px; border-radius:20px;
        border:1px solid var(--border-gold); color:var(--gold);
        background:rgba(201,168,76,0.08); margin-right:6px; margin-top:6px;
    }
    .chip {
        display:inline-block; font-family:'JetBrains Mono',monospace;
        font-size:0.68rem; background:rgba(201,168,76,0.08);
        border:1px solid var(--border-gold); color:var(--gold-light);
        padding:2px 9px; border-radius:20px; margin:2px 3px; line-height:2;
    }
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Backend stored in session_state (NOT st.cache_resource).
# This avoids the Streamlit 1.57 Windows bug where cache_resource execution
# during WebSocket handshake kills the server process silently.
# ---------------------------------------------------------------------------
def get_backend():
    if "backend" not in st.session_state:
        try:
            from backend import ResearchBackend
            b = ResearchBackend()
            b.ensure_prompts()
            st.session_state.backend = b
            st.session_state.backend_error = None
        except Exception:
            st.session_state.backend = None
            st.session_state.backend_error = traceback.format_exc()

    return st.session_state.backend, st.session_state.get("backend_error")


def init_session(backend):
    if "session" not in st.session_state:
        st.session_state.session = backend.create_session()
    if "display_messages" not in st.session_state:
        st.session_state.display_messages = []
    if "max_iterations" not in st.session_state:
        st.session_state.max_iterations = 5


def render_error_page(tb):
    st.error("Backend failed to load.")
    with st.expander("Full traceback", expanded=True):
        st.code(tb, language="python")


def render_sidebar(backend):
    with st.sidebar:
        st.title("Research Agent")
        st.caption("AGENTIC RAG SYSTEM")
        st.divider()

        if st.button("New Conversation"):
            st.session_state.session = backend.create_session()
            st.session_state.display_messages = []
            st.rerun()

        st.divider()
        st.markdown("**Settings**")
        st.session_state.max_iterations = st.slider(
            "Max Iterations", 1, 10,
            value=st.session_state.max_iterations,
        )

        st.divider()
        st.markdown("**Session**")
        msgs = st.session_state.display_messages
        n_user = sum(1 for m in msgs if m["role"] == "user")
        c1, c2 = st.columns(2)
        c1.metric("Messages", len(msgs))
        c2.metric("Queries", n_user)
        session = st.session_state.get("session")
        if session:
            st.caption(f"ID: {session.session_id}")

        prompts = backend.list_available_prompts()
        if prompts:
            st.divider()
            st.markdown("**Prompt Files**")
            chips = "".join(f'<span class="chip">{p}</span>' for p in prompts)
            st.markdown(chips, unsafe_allow_html=True)

        st.divider()
        st.caption("Powered by LangGraph, ChromaDB, Groq")


def render_welcome():
    st.markdown("""
    <div class="welcome-card">
        <h2>Research Agent</h2>
        <p>An agentic RAG system that iteratively retrieves, critiques,
        and synthesises answers powered by LangGraph, ChromaDB, and Groq.</p>
        <p style="margin-top:1rem;color:#484f58 !important;font-size:0.78rem !important;">
        Try asking: Attention in Vision Transformers, Diffusion vs GANs, RLHF alignment</p>
    </div>
    """, unsafe_allow_html=True)


def render_chat_history():
    for msg in st.session_state.display_messages:
        role = msg["role"]
        with st.chat_message(role):
            st.markdown(msg["content"])
            if role == "assistant":
                tags = []
                if msg.get("iterations") is not None:
                    tags.append(f'<span class="meta-tag">Iterations: {msg["iterations"]}</span>')
                if msg.get("draft_count") is not None:
                    tags.append(f'<span class="meta-tag">Drafts: {msg["draft_count"]}</span>')
                if tags:
                    st.markdown("".join(tags), unsafe_allow_html=True)


def handle_query(query, backend):
    session = st.session_state.session
    backend.add_user_message(session, query)
    st.session_state.display_messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        slot = st.empty()
        tokens = []
        start = time.time()

        try:
            for token in backend.stream_response(    # ← back to single value
                session, query,
                max_iterations=st.session_state.max_iterations,
            ):
                tokens.append(token)
                slot.markdown("".join(tokens) + "|")
        except Exception as e:
            slot.error(f"Stream error: {e}")
            st.code(traceback.format_exc())
            return

        end = time.time()
        full_text = "".join(tokens)
        slot.markdown(full_text)

        final_state = backend.workflow.get_state(
            session.config
        ).values

        critique_score = final_state.get("critique_score", 0)
        iterations     = final_state.get("iterations", 1)
        draft_count    = len(final_state.get("draft_answer", []))

        tags = []
        if iterations is not None:
            tags.append(f'<span class="meta-tag">Iterations: {iterations}</span>')
        if draft_count:
            tags.append(f'<span class="meta-tag">Drafts: {draft_count}</span>')
        if tags:
            st.markdown("".join(tags), unsafe_allow_html=True)

        try:
            log_to_bigquery(
                query=query,
                latency_ms=round((end - start) * 1000, 2),
                critique_score=critique_score,
                iterations=iterations,
                final_answer=full_text
            )
        except Exception as e:
            print(f"BigQuery logging failed: {e}")

    st.session_state.display_messages.append({
        "role": "assistant",
        "content": full_text,
        "iterations": iterations,
        "draft_count": draft_count,
    })


def main():
    inject_css()

    backend, error = get_backend()

    if error:
        render_error_page(error)
        return

    init_session(backend)
    render_sidebar(backend)

    st.markdown("""
    <div class="main-header">
        <h1>Research Agent</h1>
        <p>Agentic Retrieval-Augmented Generation</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.display_messages:
        render_welcome()
    else:
        render_chat_history()

    query = st.chat_input("Ask anything about your research domain...")
    if query and query.strip():
        handle_query(query.strip(), backend)


main()