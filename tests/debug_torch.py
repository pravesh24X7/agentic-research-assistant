import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

print("1. importing torch...")
import torch
print("2. torch ok")

print("3. importing SentenceTransformer directly...")
from sentence_transformers import SentenceTransformer
print("4. import ok")

print("5. loading model on CPU...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
print("6. model loaded!")

print("7. encoding test...")
result = model.encode("hello world")
print("8. encode ok:", result.shape)

print("9. moving to CUDA...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cuda")
print("10. cuda model loaded!")

print("11. encoding on cuda...")
result = model.encode("hello world")
print("12. ALL OK:", result.shape)