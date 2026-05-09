import os

from langchain_groq import ChatGroq

from src.config.settings import LLM_MODEL


KEY = os.environ["OPEN_ROUTER"]


def llm_model():
    return ChatGroq(
        model=LLM_MODEL,
        temperature=0.5,
    )