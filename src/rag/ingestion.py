import pandas as pd

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.data.data_loading import load_efficiently
from src.embedding.embedding_model import get_model


def to_documents(df: pd.DataFrame):
    
    df = df.copy()
    df['text'] = (
        df['title'].fillna('')
          + "\n\n" + 
          df['abstract'].fillna('')
    )

    result = df[ ['id', 'text', 'categories', 'update_date', 'license' ] ]

    docs = []

    for row in result.itertuples(index=False):
        docs.append(
            Document(page_content=row.text,
                     metadata={
                         'id': row.id,
                         'category': row.categories,
                         'update_date': str(row.update_date),
                         'license': row.license
                     })
        )

    return docs


def create_vector_store(storepath: str, filepath: str, embedding_model):
    
    vector_store = Chroma(
            embedding_function=embedding_model,
            persist_directory=storepath,
            collection_name="ai_ml"
        )
    
    for chunk in load_efficiently(filepath=filepath):
        docs = to_documents(chunk)
        vector_store.add_documents(docs)
    
    return vector_store