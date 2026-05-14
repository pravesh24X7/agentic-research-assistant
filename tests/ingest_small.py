import os
import pandas as pd

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.embedding.embedding_model import get_model
from src.data.data_loading import load_efficiently
from src.config.settings import SMALL_COLLECTION_NAME, SMALL_VECTOR_STORE, DATAFILE_PATH
from src.utils.logger import get_logger


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
                         'id': str(row.id),
                         'category': row.categories,
                         'update_date': str(row.update_date),
                         'license': row.license
                     })
        )

    return docs


def create_vector_store(storepath: str, filepath: str, embedding_model):

    if not os.path.exists(SMALL_COLLECTION_NAME):
        os.makedirs(SMALL_COLLECTION_NAME)

    vector_store = Chroma(
            embedding_function=embedding_model,
            persist_directory=storepath,
            collection_name=SMALL_COLLECTION_NAME
        )
    
    total_count = 0
    final_count = 5000
    
    for chunk in load_efficiently(filepath=filepath):
        docs = to_documents(chunk)
        vector_store.add_documents(docs)
        total_count += len(docs)

        if total_count > final_count:
            break
    
    return vector_store



def main():
    create_vector_store(
        storepath=SMALL_VECTOR_STORE,
        filepath=DATAFILE_PATH,
        embedding_model=get_model()
    )

    print("[*] SMALL VECTORE STORE CREATED !!!")


if __name__ == "__main__":
    main()