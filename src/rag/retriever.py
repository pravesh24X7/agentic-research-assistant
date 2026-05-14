from functools import lru_cache
from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors.chain_extract import LLMChainExtractor
from langchain_chroma import Chroma

from src.embedding.embedding_model import get_model
from src.model.chat_model import llm_model
from src.config.settings import VECTOR_STORE_DIRECTORY, COLLECTION_NAME, SMALL_VECTOR_STORE, SMALL_COLLECTION_NAME


@lru_cache(maxsize=1)
def get_vector_store():
    return Chroma(
        collection_name=SMALL_COLLECTION_NAME,
        persist_directory=SMALL_VECTOR_STORE,
        embedding_function=get_model(),
    )


def get_retriever():
    return get_vector_store().as_retriever(
        search_type="mmr",
        search_kwargs={
            'k': 5,
            'fetch_k': 15
        }
    )