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
    traceback.print_exc()
    raise

try:
    from backend import ResearchBackend
    print("DEBUG: backend imported")
except Exception:
    traceback.print_exc()
    raise

st.set_page_config(
    page_title="Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

import time


# ─── CSS ─────────────────────────────────────────────────────────────────────

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

    /* ── Sidebar ── */
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

    /* ── Buttons ── */
    .stButton>button {
        width:100%;
        background:linear-gradient(135deg,var(--gold-dim),var(--gold)) !important;
        color:#0d1117 !important; font-weight:600 !important;
        border:none !important; border-radius:10px !important;
        transition: opacity 0.2s;
    }
    .stButton>button:hover { opacity:0.82 !important; }

    /* ── Conversation history button in sidebar ── */
    .conv-btn>button {
        background:transparent !important;
        color:var(--text-secondary) !important;
        font-size:0.8rem !important;
        border:1px solid var(--border) !important;
        border-radius:8px !important;
        text-align:left !important;
        padding:6px 10px !important;
        margin-bottom:4px !important;
        font-weight:400 !important;
    }
    .conv-btn>button:hover {
        border-color:var(--border-gold) !important;
        color:var(--gold-light) !important;
        background:rgba(201,168,76,0.06) !important;
    }
    .conv-btn-active>button {
        border-color:var(--gold) !important;
        color:var(--gold-light) !important;
        background:rgba(201,168,76,0.10) !important;
    }

    /* ── Chat messages ── */
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

    /* ── Chat input ── */
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

    /* ── Page header ── */
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

    /* ── Welcome card ── */
    .welcome-card {
        max-width:540px; margin:2.5rem auto; background:#1a2236;
        border:1px solid var(--border-gold); border-radius:18px;
        padding:2rem 1.8rem; text-align:center;
    }
    .welcome-card h2 {
        font-family:'Playfair Display',serif; color:var(--gold-light);
        font-size:1.4rem; margin:0.4rem 0 0.8rem;
    }
    .welcome-card p { color:var(--text-secondary) !important; font-size:0.88rem !important; line-height:1.7; }

    /* ── Meta tags below assistant message ── */
    .meta-tag {
        display:inline-block; font-family:'JetBrains Mono',monospace;
        font-size:0.68rem; padding:2px 9px; border-radius:20px;
        border:1px solid var(--border-gold); color:var(--gold);
        background:rgba(201,168,76,0.08); margin-right:6px; margin-top:6px;
    }

    /* ── Prompt file chips ── */
    .chip {
        display:inline-block; font-family:'JetBrains Mono',monospace;
        font-size:0.68rem; background:rgba(201,168,76,0.08);
        border:1px solid var(--border-gold); color:var(--gold-light);
        padding:2px 9px; border-radius:20px; margin:2px 3px; line-height:2;
    }

    /* ── Live stage status pill ── */
    .stage-status {
        display:inline-flex; align-items:center; gap:8px;
        font-family:'JetBrains Mono',monospace; font-size:0.76rem;
        color:var(--gold-light);
        background:rgba(201,168,76,0.08);
        border:1px solid var(--border-gold);
        border-radius:20px; padding:6px 16px; margin:6px 0;
        animation:pulse 1.2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%,100% { opacity:1; }
        50%      { opacity:0.45; }
    }

    /* ── Completed stage history ── */
    .stage-done {
        display:inline-flex; align-items:center; gap:6px;
        font-family:'JetBrains Mono',monospace; font-size:0.7rem;
        color:var(--text-muted);
        padding:3px 10px; margin:2px 0;
    }

    /* ── Topic name input ── */
    [data-testid="stTextInput"] input {
        background:var(--bg-tertiary) !important;
        color:var(--text-primary) !important;
        border:1px solid var(--border-gold) !important;
        border-radius:8px !important;
        font-family:'DM Sans',sans-serif !important;
        font-size:0.82rem !important;
    }

    /* ── Toggle ── */
    [data-testid="stToggle"] label {
        color:var(--gold-light) !important;
        font-size:0.82rem !important;
        font-family:'JetBrains Mono',monospace !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ─── Session / backend helpers ────────────────────────────────────────────────

def get_backend():
    if "backend" not in st.session_state:
        try:
            b = ResearchBackend()
            b.ensure_prompts()
            st.session_state.backend = b
            st.session_state.backend_error = None
        except Exception:
            st.session_state.backend = None
            st.session_state.backend_error = traceback.format_exc()
    return st.session_state.backend, st.session_state.get("backend_error")


def init_state(backend):
    """Initialise all top-level session_state keys exactly once."""
    if "conversations" not in st.session_state:
        # list of SessionState objects, newest first
        first = backend.create_session(topic="New Chat")
        st.session_state.conversations = [first]
        st.session_state.active_idx = 0
        # per-session display messages: { session_id: [msg_dict, ...] }
        st.session_state.display_messages = {first.session_id: []}

    if "max_iterations" not in st.session_state:
        st.session_state.max_iterations = 5
    if "use_web_search" not in st.session_state:
        st.session_state.use_web_search = False


def active_session():
    return st.session_state.conversations[st.session_state.active_idx]


def active_messages():
    sid = active_session().session_id
    return st.session_state.display_messages.get(sid, [])


def push_message(msg_dict: dict):
    sid = active_session().session_id
    st.session_state.display_messages.setdefault(sid, []).append(msg_dict)


# ─── Sidebar ─────────────────────────────────────────────────────────────────

def render_sidebar(backend):
    with st.sidebar:
        st.title("Research Agent")
        st.caption("AGENTIC RAG SYSTEM")
        st.divider()

        # ── New conversation ──────────────────────────────────────────────
        if st.button("＋  New Conversation"):
            new_sess = backend.create_session(topic="New Chat")
            st.session_state.conversations.insert(0, new_sess)
            st.session_state.active_idx = 0
            st.session_state.display_messages[new_sess.session_id] = []
            st.rerun()

        st.divider()

        # ── Topic name of current chat ────────────────────────────────────
        cur = active_session()
        new_topic = st.text_input(
            "Chat topic",
            value=cur.topic,
            key=f"topic_input_{cur.session_id}",
            placeholder="Name this conversation…",
        )
        if new_topic and new_topic != cur.topic:
            cur.topic = new_topic          # mutate in-place (dataclass)

        st.divider()

        # ── Conversation history list ─────────────────────────────────────
        st.markdown("**Conversations**")
        for i, sess in enumerate(st.session_state.conversations):
            n_msgs = len(st.session_state.display_messages.get(sess.session_id, []))
            label  = f"{'▶ ' if i == st.session_state.active_idx else ''}{sess.topic}  ({n_msgs // 2} msg{'s' if n_msgs // 2 != 1 else ''})"
            css_class = "conv-btn-active" if i == st.session_state.active_idx else "conv-btn"
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(label, key=f"conv_{sess.session_id}"):
                st.session_state.active_idx = i
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        # ── Settings ──────────────────────────────────────────────────────
        st.markdown("**Settings**")
        st.session_state.max_iterations = st.slider(
            "Max Iterations", 1, 10, value=st.session_state.max_iterations,
        )
        st.session_state.use_web_search = st.toggle(
            "🌐 Web Search",
            value=st.session_state.use_web_search,
            help="When ON, the agent also queries Tavily web search.",
        )

        # ── Stats ─────────────────────────────────────────────────────────
        st.divider()
        msgs   = active_messages()
        n_user = sum(1 for m in msgs if m["role"] == "user")
        c1, c2 = st.columns(2)
        c1.metric("Messages", len(msgs))
        c2.metric("Queries",  n_user)

        prompts = backend.list_available_prompts()
        if prompts:
            st.divider()
            st.markdown("**Prompt Files**")
            chips = "".join(f'<span class="chip">{p}</span>' for p in prompts)
            st.markdown(chips, unsafe_allow_html=True)

        st.divider()
        st.caption("Powered by LangGraph · ChromaDB · Groq")


# ─── Chat rendering ───────────────────────────────────────────────────────────

def render_welcome():
    st.markdown("""
    <div class="welcome-card">
        <h2>Research Agent</h2>
        <p>An agentic RAG system that iteratively retrieves, critiques,
        and synthesises answers — powered by LangGraph, ChromaDB, and Groq.</p>
        <p style="margin-top:1rem;color:#484f58 !important;font-size:0.78rem !important;">
        Try: Attention in Vision Transformers · Diffusion vs GANs · RLHF alignment</p>
    </div>
    """, unsafe_allow_html=True)


def render_chat_history():
    for msg in active_messages():
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                _render_meta_tags(msg)


def _render_meta_tags(msg: dict):
    tags = []
    if msg.get("iterations") is not None:
        tags.append(f'<span class="meta-tag">Iterations: {msg["iterations"]}</span>')
    if msg.get("draft_count") is not None:
        tags.append(f'<span class="meta-tag">Drafts: {msg["draft_count"]}</span>')
    if msg.get("web_search_used"):
        tags.append('<span class="meta-tag">🌐 Web Search</span>')
    if tags:
        st.markdown("".join(tags), unsafe_allow_html=True)


# ─── Query handler ────────────────────────────────────────────────────────────

def handle_query(query: str, backend):
    session         = active_session()
    use_web_search  = st.session_state.use_web_search

    # Auto-name the conversation from the first query
    if session.topic == "New Chat":
        # Truncate to ~40 chars for the sidebar label
        session.topic = query[:40] + ("…" if len(query) > 40 else "")

    backend.add_user_message(session, query)
    push_message({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        # Two slots: one for the live stage pill, one for the final answer
        status_slot = st.empty()
        stages_log  = st.empty()   # optional: shows completed stages as grey text
        answer_slot = st.empty()

        completed_stages: list[str] = []
        final_text = ""
        start = time.time()

        try:
            for token, status in backend.stream_response(
                session,
                query,
                max_iterations=st.session_state.max_iterations,
                use_web_search=use_web_search,
            ):
                if status:
                    # Show current stage as pulsing pill
                    status_slot.markdown(
                        f'<div class="stage-status">{status}</div>',
                        unsafe_allow_html=True,
                    )
                    # Accumulate completed stage log shown dimly above
                    completed_stages.append(status)
                    stages_html = "".join(
                        f'<div class="stage-done">✓ {s}</div>'
                        for s in completed_stages[:-1]   # all but the current one
                    )
                    if stages_html:
                        stages_log.markdown(stages_html, unsafe_allow_html=True)

                elif token:
                    final_text += token

        except Exception as e:
            status_slot.empty()
            stages_log.empty()
            answer_slot.error(f"Stream error: {e}")
            st.code(traceback.format_exc())
            return

        # Clear live indicators; render final answer once
        status_slot.empty()
        stages_log.empty()
        answer_slot.markdown(final_text)

        # Metadata tags
        final_state = session.workflow.get_state(session.config).values
        iterations  = final_state.get("iterations", 1)
        draft_count = len(final_state.get("draft_answer") or [])

        tags = []
        if iterations is not None:
            tags.append(f'<span class="meta-tag">Iterations: {iterations}</span>')
        if draft_count:
            tags.append(f'<span class="meta-tag">Drafts: {draft_count}</span>')
        if use_web_search:
            tags.append('<span class="meta-tag">🌐 Web Search</span>')
        if tags:
            st.markdown("".join(tags), unsafe_allow_html=True)

    push_message({
        "role":           "assistant",
        "content":        final_text,
        "iterations":     iterations,
        "draft_count":    draft_count,
        "web_search_used": use_web_search,
    })


def render_error_page(tb):
    st.error("Backend failed to load.")
    with st.expander("Full traceback", expanded=True):
        st.code(tb, language="python")


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    inject_css()

    backend, error = get_backend()
    if error:
        render_error_page(error)
        return

    init_state(backend)
    render_sidebar(backend)

    st.markdown("""
    <div class="main-header">
        <h1>Research Agent</h1>
        <p>Agentic Retrieval-Augmented Generation</p>
    </div>
    """, unsafe_allow_html=True)

    if not active_messages():
        render_welcome()
    else:
        render_chat_history()

    query = st.chat_input("Ask anything about your research domain…")
    if query and query.strip():
        handle_query(query.strip(), backend)


main()