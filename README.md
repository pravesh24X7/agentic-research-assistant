# Agentic Research Assistant  
### Multi-Agent RAG Pipeline with LangGraph, ChromaDB, Groq & Streamlit  

> A modular research-focused AI system that performs iterative retrieval, summarization, critique, synthesis, and final answer generation using an agentic workflow architecture.

---

## Overview  

This project is a full-stack **Agentic Retrieval-Augmented Generation (RAG)** framework designed for deep research tasks.  
Instead of generating a single-pass answer, the system uses multiple specialized agents that work together through **LangGraph state orchestration**.

### Core Pipeline:
**Retriever → Summarizer → Critique Agent → Synthesiser → Final Answer**

This allows:
- Multi-step reasoning  
- Iterative answer improvement  
- Retrieval-grounded outputs  
- Stateful checkpointing with SQLite  
- Streamlit chat UI  
- FastAPI deployment support  

---

## Features  

### Multi-Agent Architecture
- **Retriever Agent** → Fetches relevant chunks from vector database  
- **Summary Agent** → Condenses retrieved content  
- **Critique Agent** → Evaluates answer quality  
- **Synthesiser Agent** → Improves weak drafts  
- **Final Answer Agent** → Produces polished response  

### Infrastructure
- **LangGraph** for stateful graph execution  
- **ChromaDB** for vector storage  
- **Groq LLM** for high-speed inference  
- **SQLite Checkpointer** for workflow persistence  
- **Streamlit UI** for interactive research assistant  
- **FastAPI Ready** backend architecture  

---

## Project Structure  

```bash
agentic-research-assistant/
│
├── frontend.py                # Streamlit UI
├── backend.py                 # Session + workflow manager
├── main.py                    # CLI / testing entrypoint
├── pyproject.toml             # Dependency management
├── README.md
│
├── prompts/                   # Prompt templates
│   ├── base_prompt.json
│   ├── summary_prompt.json
│   ├── critique_prompt.json
│   └── synthesiser_prompt.json
│
├── src/
│   ├── config/                # Global settings
│   ├── data/                  # Data loaders
│   ├── embedding/             # Embedding pipeline
│   ├── graphs/                # LangGraph nodes + edges + state
│   ├── model/                 # LLM + execution chain
│   ├── prompt/                # Prompt generation
│   ├── rag/                   # Retriever + vector store
│   └── utils/                 # Logger, UUID, file loader
│
├── vector_store/              # ChromaDB persistent store
├── db/                        # SQLite research checkpoints
├── notebooks/                 # Experimentation notebooks
├── notes/                     # Research notes
└── tests/                     # Debug + validation scripts
````

---

## Installation

### 1. Clone Repository

```bash
git clone <your_repo_url>
cd agentic-research-assistant
```

### 2. Create Virtual Environment

```bash
python -m venv virtual_env001
source virtual_env001/bin/activate
```

**Windows (PowerShell):**

```powershell
virtual_env001\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -e .
```

Or:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
DB_NAME=db/research.db
SAVE_PROMPT_TO=prompts
VECTOR_STORE_PATH=vector_store
```

---

## Running the Project

## Streamlit UI

```bash
streamlit run frontend.py --server.headless true --browser.gatherUsageStats false
```

---

## FastAPI Backend

```bash
uvicorn main:app --reload
```

---

## Testing Workflow

```bash
python -m tests.testing_workflow
```

---

## Agent Workflow Logic

```text
User Query
   ↓
Retriever
   ↓
Summary
   ↓
Critique
   ↓
Synthesiser
   ↓
Final Answer
```

### Evaluation Loop:

* If critique score is weak → Re-synthesise
* If critique score is strong → Finalize answer

---

## Example Research Queries

* Attention Mechanism in Vision Transformer
* Diffusion Models vs GANs
* RLHF in LLM Alignment
* Federated Learning in Healthcare
* Explainable AI in Medical Imaging

---

## Performance Notes

### Optimizations:

* `@lru_cache` for graph + prompt reuse
* Shared SQLite checkpointer
* Prewarmed vector store + Groq client
* Stable Streamlit version (`1.44.1`)
* Disabled watcher for Windows stability

---

## Known Issues

### Streamlit 1.45+ Crash on Some Windows Systems

**Fix:**

```bash
pip install streamlit==1.44.1
```

---

## Future Improvements

* PDF / DOCX research exports
* Multi-user authentication
* Docker deployment
* Kubernetes scaling

---

## Tech Stack

| Layer         | Technology            |
| ------------- | --------------------- |
| UI            | Streamlit             |
| API           | FastAPI               |
| Orchestration | LangGraph             |
| LLM           | Groq                  |
| Vector DB     | ChromaDB              |
| Storage       | SQLite                |
| Embeddings    | Sentence Transformers |

---

## Author

**Pravesh**
AI/ML Research Builder

---

## Final Note

This project is built for **serious research workflows**, not simple chatbot interaction.
Its strength comes from **iterative reasoning + retrieval grounding + critique loops**, making it useful for:

* Academic research
* Technical exploration
* Knowledge synthesis
* Experimental RAG systems