from src.config.settings import SAVE_PROMPT_TO
from src.model.execution_chain import chain
from src.prompt.generate_prompt import create_prompt

def main():

    name = f"{SAVE_PROMPT_TO}base_prompt.json"
    create_prompt(name=name)

    query = "What is capital city of India?"
    execution_chain = chain(prompt_name=name)

    result = execution_chain.invoke({
        'query': query
    })

    print(result)



main()