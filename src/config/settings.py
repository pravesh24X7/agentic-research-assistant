import os
from dotenv import load_dotenv


load_dotenv()


VECTOR_STORE_DIRECTORY="./vector_store"
DATAFILE_PATH = "data/raw/data001.json"
COLLECTION_NAME="ai_ml"
EMBEDDING_MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL="meta-llama/llama-4-scout-17b-16e-instruct"
DB_NAME="db/research.db"
SAVE_PROMPT_TO = os.path.join("prompts")