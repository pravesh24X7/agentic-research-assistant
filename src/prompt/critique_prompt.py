from langchain_core.prompts import PromptTemplate


def create_cirtique_prompt(name: str):

    template="""
You are a strict scientific reviewer. Below is a question and a draft answer 
based on research papers.

Question: {query}
Draft answer: {draft_answer}

Your job:
- Identify what is missing or incomplete in the draft
- Point out any unsupported claims
- Note if the question was not fully answered
- Suggest what additional information would strengthen the answer

Be specific and harsh. Write your critique as bullet points.
    """
   
    critique_prompt = PromptTemplate(template=template,
                                   validate_template=True,
                                   input_variables=['query', 'draft_answer'])
    critique_prompt.save(name)