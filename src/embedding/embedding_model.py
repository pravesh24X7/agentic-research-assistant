import torch

from langchain_huggingface import HuggingFaceEmbeddings


def get_model():

    device = "cuda" if torch.cuda.is_available() else "cpu"
    embedding_model = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2",
                                            model_kwargs={
                                                'device': device
                                            })
    return embedding_model
