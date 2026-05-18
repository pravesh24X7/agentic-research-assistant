# 🔬 Agentic Research Assistant
### Multi-Agent RAG System · LangGraph · ChromaDB · Gemma 4 · Streamlit

> Democratising access to 200,000+ AI/ML research papers for students worldwide — through natural language queries, multilingual support, and iterative agentic reasoning powered by Google Gemma 4.

---

## 🌍 The Problem

Over **200 million students** in developing countries cannot access academic research locked behind expensive journal paywalls — $30 to $50 per paper. This system tears that wall down.

A student in rural India can ask:

> *"अटेंशन मैकेनिज्म कैसे काम करता है?"*

And receive a **cited, research-backed answer** drawn from 200,000 real papers — in Hindi — for free — in under 8 seconds.

---

## 🧠 How It Works

The system uses a **4-node LangGraph state machine** with iterative self-refinement:

```
User Query
    ↓
Retriever          → Hybrid BM25 + Dense MMR search + Cross-Encoder Reranking
    ↓
Summariser         → Gemma 4 generates a cited draft answer
    ↓
Critic             → Scores answer 1–10 using structured rubric
    ↓
Synthesiser        → Rewrites if score < 6 (loop until quality threshold met)
    ↓
Final Answer       → Delivered with citations, grounded in real research
```

The system **never hallucinate**s — every claim is backed by a retrieved paper. If the answer is not good enough, it rejects its own output and tries again.

---

## ✨ Features

### 🤖 Multi-Agent Architecture
| Agent | Role |
|---|---|
| **Retriever** | Hybrid BM25 + dense MMR retrieval across 200K papers |
| **Summariser** | Gemma 4 generates structured, cited draft answer |
| **Critic** | Scores answer quality 1–10 with structured rubric |
| **Synthesiser** | Rewrites weak drafts based on critic feedback |
| **Final Answer** | Delivers polished, citation-grounded response |

### 🌐 Multilingual Support
Gemma 4 auto-detects query language and responds accordingly.
Tested in: **English · Hindi · French · Spanish · Arabic**

### 📄 Document Upload
Upload your own PDF papers — system retrieves across both your document and the 200K paper vector store simultaneously using hybrid retrieval.

### 🔍 Web Search Integration
Optional Tavily web search toggle for real-time information beyond the vector store.

### 📊 Full Observability
- **LangSmith** — traces every agent call, token usage, and latency
- **BigQuery** — logs query analytics for monitoring and analysis

---

## 📁 Project Structure

```
agentic-research-assistant/
│
├── frontend.py                   # Streamlit chat UI
├── backend.py                    # Session + workflow manager
├── main.py                       # CLI / FastAPI entrypoint
├── requirements.txt              # Dependencies
├── .env                          # Environment variables
│
├── prompts/                      # Saved prompt templates (JSON)
│   ├── summary_prompt.json
│   ├── critique_prompt.json
│   └── synthesiser_prompt.json
│
├── src/
│   ├── config/
│   │   └── settings.py           # Global config constants
│   ├── data/
│   │   └── data_loading.py       # arXiv JSON chunked loader
│   ├── embedding/
│   │   └── embedding_model.py    # SentenceTransformer wrapper
│   ├── graphs/
│   │   ├── state.py              # AgentState TypedDict
│   │   ├── nodes.py              # All agent node functions
│   │   ├── edges.py              # Conditional routing logic
│   │   └── main_graph.py        # Graph compilation
│   ├── model/
│   │   ├── chat_model.py         # Gemma 4 via Google GenAI
│   │   ├── critique_structure.py # Pydantic output schema
│   │   └── execution_chain.py    # Prompt | LLM | Parser chains
│   ├── prompt/
│   │   ├── summarizer_prompt.py
│   │   ├── critique_prompt.py
│   │   └── synthesiser_prompt.py
│   ├── rag/
│   │   ├── ingestion.py          # arXiv → ChromaDB ingestion
│   │   ├── retriever.py          # MMR retriever + cross-encoder
│   │   └── uploaded_doc.py       # Per-session PDF retriever
│   ├── tools/
│   │   └── search.py             # Tavily web search tool
│   └── utils/
│       ├── bq_logger.py          # BigQuery async logger
│       ├── file_loader.py        # Prompt JSON loader
│       ├── logger.py             # Python logging setup
│       └── generate_uuid.py      # Thread ID generator
│
├── vector_store_small/           # ChromaDB persistent store
├── db/                           # SQLite checkpoints
├── data/
│   └── raw/data001.json          # arXiv dataset
└── notebooks/                    # Kaggle submission notebook
```

---

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/pravesh24X7/agentic-research-assistant
cd agentic-research-assistant
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_google_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
TAVILY_API_KEY=your_tavily_api_key
```

---

## 🚀 Running the Project

### Streamlit UI
```bash
streamlit run frontend.py
```

### FastAPI Backend
```bash
uvicorn main:app --reload
```

---

## 📈 Performance

| Metric | Value |
|---|---|
| Average end-to-end latency | ~7.8 seconds |
| Critic score on first pass | 6.5 / 10 |
| Loop exit on first pass | 80% of queries |
| Retrieval latency | ~1.1s with cross-encoder |
| Papers indexed | 200,000+ arXiv CS/AI abstracts |
| Languages supported | EN · HI · FR · ES · AR |

### Optimizations Applied
- `@lru_cache` on embedding model, vector store, graph, and prompts
- `TEMPERATURE = 0.0` for faster deterministic responses
- `max_output_tokens = 512` cap on LLM calls
- Cross-encoder reranking limited to top-5 candidates
- BigQuery logging runs async in background thread (fire-and-forget)
- `MemorySaver` checkpointer — no disk I/O overhead

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Gemma 4 (via Google GenAI) |
| Orchestration | LangGraph |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Reranking | BAAI/bge-reranker-base |
| Web Search | Tavily |
| Observability | LangSmith + BigQuery |
| UI | Streamlit |
| API | FastAPI |
| Data | arXiv (200K CS/AI abstracts) |

---

## 🔗 Links

- 🌐 **Live Demo:** https://agentic-research-assistant-prvsh2407.streamlit.app/
- 💻 **GitHub:** https://github.com/pravesh24X7/agentic-research-assistant
- 📓 **Demo Video:** https://drive.google.com/file/d/19zR5rpeSzrjy1Zq6aPliQr3pNWXfMYfp/view?usp=drive_link 

---

## 📌 Note

This project was built using the **Gemma 4** with a singular mission — to make research accessible to every student on the planet, regardless of where they live or what they can afford.
