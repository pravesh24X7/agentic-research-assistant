from langchain_core.prompts import PromptTemplate


def create_cirtique_prompt(name: str):

    template="""
You are a scientific reviewer evaluating a research answer.

Question: {query}
Draft answer: {draft_answer}

Score the answer using this EXACT rubric:
- Score 1-3: Answer is completely wrong, off-topic, or missing core concepts
- Score 4-5: Answer covers basics but lacks depth, citations, or structure  
- Score 6-7: Answer is solid with good structure, some citations, addresses the question well
- Score 8-9: Answer is comprehensive, well-cited, mathematically precise where needed
- Score 10: Publication-ready, exhaustive, no meaningful improvements possible

IMPORTANT RULES:
- If the answer correctly explains the core concept, minimum score is 5
- If the answer includes mathematical formulation, add +1 to your score
- If the answer includes citations, add +1 to your score  
- If the answer addresses limitations and future work, add +1 to your score
- Do NOT penalise for information not present in the source documents
- Compare this answer to the PREVIOUS iteration — if it improved, score must be HIGHER

Current iteration: {iterations}

Instructions:
{instructions}
    """
   
    critique_prompt = PromptTemplate(template=template,
                                   validate_template=True,
                                   input_variables=['query', 'draft_answer', 'instructions', 'iterations'])
    critique_prompt.save(name)