import os
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

from src.graphs.main_graph import build_graph
from src.utils.generate_uuid import get_unique_id
from src.utils.logger import get_logger
from src.utils.bq_logger import log_to_bigquery

from src.prompt.critique_prompt import create_cirtique_prompt
from src.prompt.summarizer_prompt import create_summary_prompt
from src.prompt.synthesiser_prompt import create_synthesiser_prompt

from src.config.settings import SAVE_PROMPT_TO


# request schema
class QueryRequest(BaseModel):
    query: str
    max_iterations: int = 5


# global logger and workflow object
logger = get_logger()
workflow = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global workflow

    logger.debug("[*] Starting FastAPI service ...")

    logger.debug("[+] Running `PRE-WARMING` stage")
    from src.rag.retriever import get_vector_store
    from src.model.chat_model import llm_model

    get_vector_store()
    llm_model()

    logger.debug("[*] STAGE EXECUTION FINISH")

    if not os.path.exists(SAVE_PROMPT_TO):
        os.makedirs(SAVE_PROMPT_TO)
    
    summary=f'{SAVE_PROMPT_TO}/summary_prompt.json'
    critique=f'{SAVE_PROMPT_TO}/critique_prompt.json'
    synthesiser=f'{SAVE_PROMPT_TO}/synthesiser_prompt.json'

    all_prompts = os.listdir(SAVE_PROMPT_TO)
    logger.debug(f"[+] Available prompts are: {(','.join(all_prompts))}")

    if 'critique_prompt.json' not in all_prompts:
        logger.debug(f"\n\t[-] Generating {critique} FILE")
        create_cirtique_prompt(name=critique)
    
    if 'synthesiser_prompt.json' not in all_prompts:
        logger.debug(f"\n\t[-] Generating {synthesiser} FILE")
        create_synthesiser_prompt(name=synthesiser)
    
    if 'summary_prompt.json' not in all_prompts:
        logger.debug(f"\n\t[-] Generating {summary} FILE")
        create_summary_prompt(name=summary)

    # build graph once
    workflow = build_graph()

    logger.debug("[*] FastAPI service ready to use ...")
    yield

    logger.debug("[*] Shutting down FastAPI service ...")


app = FastAPI(
    title="Multi agent research API",
    description="LangGraph + RAG research assistant.",
    version="1.0.1",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        'status': 'running',
        'message': 'Multi agent research API service live.'
    }


@app.post("/research")
async def run_research(request: QueryRequest):
    global workflow

    try:
        unique_id = get_unique_id()
        config = {
            'configurable': {
                'thread_id': unique_id
            },
            'metadata': {
                'thread_id': unique_id
            },
            'run_name': "agentic-workflow-api"
        }

        initial_state = {
            'query': request.query,
            'max_iterations': request.max_iterations,
            'iterations': 0
        }

        streamed_output = []

        start = time.time()

        # stream workflow response
        for message_chunk, _ in workflow.stream(initial_state, config=config, stream_mode='messages'):
            if message_chunk.content:
                streamed_output.append(message_chunk.content)
        
        final_state = workflow.get_state(config=config).values

        latency_ms = (time.time() - start) * 1000

        log_to_bigquery(
            query=request.question,
            latency_ms=latency_ms,
            critique_score=final_state.get("critique_score", 0),
            iterations=final_state.get("iterations", 0),
            final_answer=final_state.get("final_answer", "")
        )

        return {
            'thread_id': unique_id,
            'query': request.query,
            'iterations': final_state.get('iterations', 0),
            'streamed_response': "".join(streamed_output),
            'draft_answer': final_state.get('draft_answer', []),
            'final_answer': final_state.get('final_answer', ""),
            'critique': final_state.get('critique', ''),
            'critique_score': final_state.get('critique_score', 0),
        }

    except Exception as e:
        logger.exception("[-] Execution failed at `run_research` function")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )

@app.get("/session/{thread_id}")
async def get_session(thread_id: str):
    
    final_state = workflow.get_state(config={
        'configurable': {'thread_id': thread_id}
    })

    return {
        "thread_id": thread_id,
        "message": final_state.final_answer,
        "critique_score": final_state.get("critique_score", 0),
        "critique": final_state.get("critique", "")
    }