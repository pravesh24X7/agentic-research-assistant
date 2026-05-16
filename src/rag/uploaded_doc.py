from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_classic.retrievers import BM25Retriever, EnsembleRetriever

from src.embedding.embedding_model import get_model


def build_uploaded_doc_retriever(
        uploaded_files,
        session_id
):

    if not uploaded_files:
        return None

    splitter=RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    all_chunks=[]

    for file in uploaded_files:

        loader=PyPDFLoader(file)

        pages=loader.load()

        chunks=splitter.split_documents(
            pages
        )

        for i,chunk in enumerate(chunks):

            chunk.metadata["source"]=(

                Path(file).name
            )

            chunk.metadata["chunk_id"]=i

            chunk.metadata["page"]=(
                chunk.metadata.get(
                    "page",
                    0
                )+1
            )

        all_chunks.extend(
            chunks
        )

    temp_db=Chroma.from_documents(
        documents=all_chunks,
        embedding=get_model(),
        collection_name=f"session_{session_id}"
    )

    dense_retriever = (
        temp_db.as_retriever(
            search_type="mmr",
            search_kwargs={
                'k': 10,
                'fetch_k': 20
            }
        )
    )

    bm25_retriever = BM25Retriever.from_documents(all_chunks)
    bm25_retriever.k = 10

    hybrid_retriever = EnsembleRetriever(retrievers=[
        dense_retriever, bm25_retriever
    ],
    weights=[0.7, 0.3])

    return hybrid_retriever