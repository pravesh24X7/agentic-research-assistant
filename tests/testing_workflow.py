import os

from src.graphs.main_graph import build_graph
from src.utils.generate_uuid import get_unique_id
from src.utils.logger import get_logger
from src.prompt.critique_prompt import create_cirtique_prompt
from src.prompt.summarizer_prompt import create_summary_prompt
from src.prompt.synthesiser_prompt import create_synthesiser_prompt
from src.config.settings import SAVE_PROMPT_TO


UNIQUE_SESSION_ID=get_unique_id()
CONFIG={
    'configurable': {
        'thread_id': UNIQUE_SESSION_ID
    },
    'metadata': {
        'thread_id': UNIQUE_SESSION_ID
    },
    'run_name': 'agentic-worfklow-testfile'
}

def main():

    logger = get_logger()
    logger.debug('\n\n[*] Begin Execution ...')

    logger.debug("Pre-warming retriever and LLM...")
    from src.rag.retriever import get_vector_store
    from src.model.chat_model import llm_model
    get_vector_store()   # loads ChromaDB + embedding model into lru_cache
    llm_model()          # initialises Groq connection
    logger.debug("Pre-warming complete.")

    if not os.path.exists(SAVE_PROMPT_TO):
        os.makedirs(SAVE_PROMPT_TO)

    summary=f'{SAVE_PROMPT_TO}/summary_prompt.json'
    critique=f'{SAVE_PROMPT_TO}/critique_prompt.json'
    synthesiser=f'{SAVE_PROMPT_TO}/synthesiser_prompt.json'

    all_prompts = os.listdir(SAVE_PROMPT_TO)
    print("Available Prompts are :", all_prompts, end="\n\n\n")

    if 'critique_prompt.json' not in all_prompts:
        logger.debug(f"\n\t[-] Generating {critique} FILE")
        create_cirtique_prompt(name=critique)
    
    if 'synthesiser_prompt.json' not in all_prompts:
        logger.debug(f"\n\t[-] Generating {synthesiser} FILE")
        create_synthesiser_prompt(name=synthesiser)
    
    if 'summary_prompt.json' not in all_prompts:
        logger.debug(f"\n\t[-] Generating {summary} FILE")
        create_summary_prompt(name=summary)

    workflow = build_graph()

    initial_state = {
        'query': "Attention mechanism in Vision Transformer",
        'max_iterations': 5,
        'iterations': 0
    }
    
    for message_chunk, metadata in workflow.stream(initial_state, config=CONFIG, stream_mode="messages"):
        if message_chunk.content:
            print(message_chunk.content, end="", flush=True)
    
    print("\n", "-"*20)
    final_state = workflow.get_state(config=CONFIG).values
    print(final_state['iterations'])

    for ans in final_state['draft_answer']:
        print(ans, end="-----"*30+"\n")
    



if __name__ == '__main__':
    main()