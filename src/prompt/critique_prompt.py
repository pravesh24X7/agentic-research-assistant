from langchain_core.prompts import PromptTemplate


def create_cirtique_prompt(name: str):

    template="""
You are a strict and uncompromising scientific reviewer. Below is a question and a draft answer
based on research papers.

Question: {query}
Draft answer: {draft_answer}

Your job:
1. Critically evaluate the draft answer.
2. Identify all missing or incomplete points.
3. Point out any unsupported, inaccurate, or misleading claims.
4. Determine whether the question has been fully answered.
5. Suggest additional information or references that would strengthen the answer.
6. Be brutally honest and specific. No vague feedback.


Rules:
- The critique_score must reflect the **overall quality** of the draft answer.
- The critique must be **comprehensive**, covering every missing point, unsupported claim, and weakness.
- Use **bullet points**, each starting with "- ".

Instructions:
{instructions}
    """
   
    critique_prompt = PromptTemplate(template=template,
                                   validate_template=True,
                                   input_variables=['query', 'draft_answer', 'instructions'])
    critique_prompt.save(name)