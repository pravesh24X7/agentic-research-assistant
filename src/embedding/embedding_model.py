from langchain_huggingface import HuggingFaceEmbeddings


def get_model():
    embedding_model = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")
    return embedding_model
