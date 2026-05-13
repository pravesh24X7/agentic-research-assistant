from functools import lru_cache
from src.utils.file_loader import load_file
from langchain_core.output_parsers import StrOutputParser

from src.model.chat_model import llm_model
from src.utils.logger import get_logger

logger = get_logger()


@lru_cache(maxsize=10)
def get_prompt(name: str):
    logger.debug(f"[+] Loading {name}")
    return load_file(name)


def chain(prompt_name: str, ):

    prompt = get_prompt(prompt_name)
    parser = StrOutputParser()
    llm = llm_model()
    chain = prompt | llm | parser
    return chain
