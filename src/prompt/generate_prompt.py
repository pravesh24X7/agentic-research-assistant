from langchain_core.prompts import PromptTemplate

from src.config.settings import SAVE_PROMPT_TO


def base_prompt(name: str):
    template="""
        You're an helpful assistant, Solve user query.
        \n\n
        Query:{query}
    """
    base_prompt = PromptTemplate(template=template,
                                input_variables=['query'],
                                validate_template=True)
    base_prompt.save(name)