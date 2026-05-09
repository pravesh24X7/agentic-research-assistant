from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors.chain_extract import LLMChainExtractor
from langchain_chroma import Chroma

from src.embedding.embedding_model import get_model
from src.model.chat_model import llm_model
from src.config.settings import VECTOR_STORE_DIRECTORY, COLLECTION_NAME


def get_retriever():
    retriever = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=VECTOR_STORE_DIRECTORY,
        embedding_function=get_model()
    ).as_retriever(
        search_type="mmr",
        search_kwargs={'k': 10, 'fetch_k': 25}
    )

    llm  = llm_model()
    compressor = LLMChainExtractor.from_llm(llm=llm)
    compression_retriever = ContextualCompressionRetriever(base_retriever=retriever,
                                                           base_compressor=compressor)
    
    return compression_retriever