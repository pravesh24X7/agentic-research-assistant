import os

from functools import lru_cache
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from src.config.settings import LLM_MODEL, TEMPERATURE

API_KEY = os.getenv("GOOGLE_API_KEY")

@lru_cache(maxsize=1)
def llm_model():
    # return ChatGoogleGenerativeAI(
    #     model=LLM_MODEL,
    #     temperature=TEMPERATURE,
    #     google_api_key=API_KEY,
    # )

    return ChatGroq(model=LLM_MODEL,
                    temperature=TEMPERATURE,)
