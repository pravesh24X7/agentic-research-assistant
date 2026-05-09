from langchain_core.prompts import load_prompt
from langchain_core.output_parsers import StrOutputParser

from src.model.chat_model import llm_model


def chain(prompt_name: str, ):

    prompt = load_prompt(prompt_name)
    parser = StrOutputParser()
    llm = llm_model()

    chain = prompt | llm | parser
    return chain
