import json
import time

from langchain_core.prompts import load_prompt
from langchain_core.output_parsers import PydanticOutputParser
from langsmith import traceable

from src.rag.retriever import get_retriever
from src.graphs.state import AgentState
from src.model.execution_chain import chain
from src.model.chat_model import llm_model
from src.model.critique_structure import CritiqueStructure
from src.config.settings import SAVE_PROMPT_TO


@traceable(name='retrieval_node', metadata={"stage": "evaluation"})
# def retriever(state: AgentState) -> dict:
#     retriever = get_retriever()
#     result = retriever.invoke(state['query'])
#     return {
#         'retrieved_docs': [ doc.page_content for doc in result ]
#     }

# in retriever node
def retriever(state: AgentState) -> dict:
    start = time.time()
    r = get_retriever()
    docs = r.invoke(state['query'])
    print(f"Retriever took: {time.time()-start:.2f}s")
    return {'retrieved_docs': [doc.page_content for doc in docs]}

    
@traceable(name='summary_node', metadata={"stage": "evaluation"})
def summary(state: AgentState) -> dict:
    execution_chain = chain(f'{SAVE_PROMPT_TO}/summary_prompt.json')

    result = execution_chain.invoke({
        "query": state['query'],
        "retrieved_docs": state["retrieved_docs"], 
    },
    config={
        'tags': ['summary',],
        'metadata': {
            'iterations': state['iterations']
        }
    })

    return {
        'draft_answer': [str(result)],
    }
    

@traceable(name='critique_node', metadata={"stage": "evaluation"})
def critique(state: AgentState) -> dict:
    prompt = load_prompt(f'{SAVE_PROMPT_TO}/critique_prompt.json')

    history = state.get('critique_score_history', [])

    parser = PydanticOutputParser(pydantic_object=CritiqueStructure)

    structured_llm = llm_model()
    execution_chain = prompt | structured_llm | parser

    result = execution_chain.invoke({
        'query': state['query'],
        'draft_answer': state['draft_answer'][-1],
        'iterations': state['iterations'],
        'instructions': parser.get_format_instructions(),
    },
    config={
        'tags': ['critique'],
        'metadata': {
            'iterations': state['iterations']
        }
    })
    
    return {
        'critique_score': result.critique_score,
        'critique': result.critique,
        'critique_score_history': [result.critique_score]
    }


@traceable(name='synthesiser_node', metadata={"stage": "evaluation"})
def synthesiser(state: AgentState) -> dict:

    execution_chain = chain(f'{SAVE_PROMPT_TO}/synthesiser_prompt.json')

    result = execution_chain.invoke({
        'query': state['query'],
        'draft_answer': state['draft_answer'][-1],
        'critique': state['critique']
    }, config={
        'tags': ['synthesiser'],
        'metadata': {
            'iterations': state['iterations']
        }
    })

    return {
        'draft_answer': [result],
        'iterations': state['iterations'] + 1,
    }


@traceable(name='final_answer_node', metadata={"stage": "evaluation"})
def generate_final_answer(state: AgentState) -> dict:

    return {
        'final_answer': state['draft_answer'][-1]
    }