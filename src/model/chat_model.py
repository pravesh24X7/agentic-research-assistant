import os

from functools import lru_cache
from langchain_groq import ChatGroq
from src.config.settings import LLM_MODEL


@lru_cache(maxsize=1)       # create once, reuse forever
def llm_model():
    return ChatGroq(
        model=LLM_MODEL,
        temperature=0.5,
    )