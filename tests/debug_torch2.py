import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

print("1. importing torch...")
import torch
print("2. torch ok, device:", "cuda" if torch.cuda.is_available() else "cpu")

print("3. importing HuggingFaceEmbeddings...")
from langchain_huggingface import HuggingFaceEmbeddings
print("4. import ok")

print("5. loading model with cpu...")
model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"batch_size": 8, "normalize_embeddings": True}
)
print("6. model loaded!")

print("7. test embed...")
result = model.embed_query("hello world")
print("8. ALL OK, embedding size:", len(result))