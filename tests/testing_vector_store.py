import torch
torch.set_num_threads(1)

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from langchain_chroma import Chroma
from src.embedding.embedding_model import get_model
from src.config.settings import VECTOR_STORE_DIRECTORY, COLLECTION_NAME


def get_store():
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=VECTOR_STORE_DIRECTORY,
        embedding_function=get_model()
    )


if __name__ == "__main__":   # <-- Guard is critical on Windows

    vector_store = get_store()
    print(vector_store._collection.count())

    result = vector_store.similarity_search(
        query="ANN and SVM performance",
        k=5
    )

    print(result)