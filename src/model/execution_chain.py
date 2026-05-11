from functools import lru_cache
from langchain_core.prompts import load_prompt
from langchain_core.output_parsers import StrOutputParser

from src.model.chat_model import llm_model


@lru_cache(maxsize=10)
def get_prompt(name: str):
    return load_prompt(name)


def chain(prompt_name: str, ):

    prompt = get_prompt(prompt_name)
    parser = StrOutputParser()
    llm = llm_model()

    chain = prompt | llm | parser
    return chain
