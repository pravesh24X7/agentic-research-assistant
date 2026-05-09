from langchain_core.prompts import PromptTemplate


def create_synthesiser_prompt(name: str):
    template="""
    You are a senior research scientist writing a final answer.

Original question: {query}

A junior researcher wrote this draft:
{draft_answer}

A reviewer gave this critique:
{critique}

Your job: Write a final, polished answer that:
- Directly answers the question
- Fixes all issues raised in the critique
- Is clear and well-structured
- Stays grounded in the research evidence
- Is 200-250 words maximum

Do NOT mention the draft or critique in your answer. 
Just write the final answer directly.
    """

    synthesiser_prompt = PromptTemplate(template=template,
                                      validate_template=True,
                                      input_variables=['query', 'draft_answer', 'critique'])
    synthesiser_prompt.save(name)