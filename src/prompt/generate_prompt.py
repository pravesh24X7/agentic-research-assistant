from langchain_core.prompts import PromptTemplate

from src.config.settings import SAVE_PROMPT_TO


template="""
    You're an helpful assistant, Solve user query.
    \n\n
    Query:{query}
"""


def create_prompt(name: str):
    base_prompt = PromptTemplate(template=template,
                                input_variables=['query'],
                                validate_template=True)
    base_prompt.save(name)