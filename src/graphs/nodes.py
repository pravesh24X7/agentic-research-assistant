import json
import time

from langchain_classic.retrievers import EnsembleRetriever
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker

from langchain_core.output_parsers import PydanticOutputParser
from langsmith import traceable

from src.tools.search import search_tool
from src.utils.file_loader import load_file
from src.rag.retriever import get_retriever
from src.rag.uploaded_doc import build_uploaded_doc_retriever
from src.graphs.state import AgentState
from src.model.execution_chain import chain
from src.model.chat_model import llm_model
from src.model.critique_structure import CritiqueStructure
from src.config.settings import SAVE_PROMPT_TO


@traceable(name="build_context", metadata={"stage": "evaluation"})
def build_context(state: AgentState):
    docs = state['retrieved_docs']
    context = ""

    citation = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "arxiv")
        page = doc.metadata.get("page", "N/A")
        chunk = doc.metadata.get("chunk_id", "N/A")

        context += f"""
            [DOC{i}]
            Source: {source}
            Page: {page}
            Text: {doc.page_content}
        """

        citation.append({"source": source, "page": page, "chunk": chunk})
        return {
            "context": context,
            "citations": citation
        }


@traceable(name="search_engine_node", metadata={"stage": "evaluation"})
def search_online(state: AgentState) -> dict:
    search_results = search_tool.invoke({"search_query": state['query']})
    return {'search_results': search_results}


@traceable(name='retrieval_node', metadata={"stage": "evaluation"})
def retriever(state: AgentState) -> dict:
    query = state['query']
    r = get_retriever()     # normal retriever
    uploaded_doc_retriever = (
        build_uploaded_doc_retriever(
            uploaded_files=state.get("uploaded_files", []),
            session_id=state.get("thread_id", "default")
        )
    )
    
    retrievers = [r]
    weights = [0.6]

    if uploaded_doc_retriever:
        retrievers.append(uploaded_doc_retriever)
        weights.append(0.4)
    
    combined = EnsembleRetriever(
        retrievers=retrievers,
        weights=weights
    )

    cross_encoder = HuggingFaceCrossEncoder(model_name='BAAI/bge-reranker-base')
    
    compressor = CrossEncoderReranker(model=cross_encoder,
                                      top_n=10)
    compression_retriever = (ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=combined
    ))

    docs = compression_retriever.invoke(query)
    return {'retrieved_docs': docs}


@traceable(name='summary_node', metadata={"stage": "evaluation"})
def summary(state: AgentState) -> dict:
    execution_chain = chain(f'{SAVE_PROMPT_TO}/summary_prompt.json')

    combined_context = state.get('context', 'N/A')
    if state.get("use_web_search") and state.get("search_results"):
        combined_context += "\n\n" + (state['search_results'])
    
    citations = state.get('citations', [])
    citation_text = ""

    for i, c in enumerate(citations):
        citation_text += f"""
            [{i+1}]
            Source: {c.get('source')}
            Page: {c.get('page')}
            Chunk: {c.get('chunk')}
        """

    result = execution_chain.invoke(
        {
            "query": state['query'],
            "retrieved_docs": combined_context,
            "citation_info": citation_text
        },
        config={
            'tags': ['summary'],
            'metadata': {'iterations': state['iterations']},
        },
    )
    return {'draft_answer': [str(result)]}


@traceable(name='critique_node', metadata={"stage": "evaluation"})
def critique(state: AgentState) -> dict:
    prompt = load_file(f'{SAVE_PROMPT_TO}/critique_prompt.json')
    parser = PydanticOutputParser(pydantic_object=CritiqueStructure)
    structured_llm = llm_model()
    execution_chain = prompt | structured_llm | parser

    result = execution_chain.invoke(
        {
            'query': state['query'],
            'draft_answer': state['draft_answer'][-1],
            'iterations': state['iterations'],
            'instructions': parser.get_format_instructions(),
        },
        config={
            'tags': ['critique'],
            'metadata': {'iterations': state['iterations']},
        },
    )
    return {
        'critique_score': result.critique_score,
        'critique': result.critique,
        'critique_score_history': [result.critique_score],
    }


@traceable(name='synthesiser_node', metadata={"stage": "evaluation"})
def synthesiser(state: AgentState) -> dict:
    execution_chain = chain(f'{SAVE_PROMPT_TO}/synthesiser_prompt.json')

    result = execution_chain.invoke(
        {
            'query': state['query'],
            'draft_answer': state['draft_answer'][-1],
            'critique': state['critique'],
        },
        config={
            'tags': ['synthesiser'],
            'metadata': {'iterations': state['iterations']},
        },
    )
    return {
        'draft_answer': [result],
        'iterations': state['iterations'] + 1,
    }


@traceable(name='final_answer_node', metadata={"stage": "evaluation"})
def generate_final_answer(state: AgentState) -> dict:
    return {'final_answer': state['draft_answer'][-1]}