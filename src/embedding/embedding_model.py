import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import torch
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
from src.config.settings import EMBEDDING_MODEL_NAME


class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name: str, device: str):
        self.model = SentenceTransformer(model_name, device=device)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            batch_size=8,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embedding.tolist()


def get_model() -> Embeddings:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return SentenceTransformerEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        device=device
    )