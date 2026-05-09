from langchain_core.prompts import load_prompt

from src.rag.retriever import get_retriever
from src.graphs.state import AgentState
from src.model.execution_chain import chain
from src.model.chat_model import llm_model
from src.model.cirtique_structure import CritiqueStructure
from src.config.settings import SAVE_PROMPT_TO


def retriever(state: AgentState) -> dict:
    retriever = get_retriever()
    result = retriever.invoke(state['query'])
    return {
        result: [ doc.page_content for doc in result ]
    }
    
    

def summary(state: AgentState) -> dict:
    execution_chain = chain(f'{SAVE_PROMPT_TO}summary_prompt.json')

    result = execution_chain.invoke({
        "query": state['query'],
        "retrieved_docs": state["retrieved_docs"]
    })

    return {
        'draft_answer': result
    }
    


def critique(state: AgentState) -> dict:
    prompt = load_prompt(f'{SAVE_PROMPT_TO}critique_prompt.json')

    structured_llm = llm_model().with_structured_output(CritiqueStructure)
    execution_chain = prompt | structured_llm

    result = execution_chain.invoke({
        'query': state['query'],
        'draft_answer': state['draft_answer']
    })
    
    return {
        'critique_score': result.critique_score,
        'critique': result.critique
    }


def synthesiser(state: AgentState) -> dict:
    execution_chain = chain(f'{SAVE_PROMPT_TO}synthesiser_prompt.json')

    result = execution_chain.invoke({
        'query': state['query'],
        'draft_answer': state['draft_answer'],
        'critique': state['critique']
    })

    return {
        'final_answer': result
    }