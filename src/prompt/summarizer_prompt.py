from langchain_core.prompts import PromptTemplate


def create_summary_prompt(name: str):
    template="""
You are a research assistant. Using ONLY the following research paper excerpts, 
write a comprehensive answer to this question: {query}

Research excerpts:
{retrieved_docs}

Rules:
- Only use information from the excerpts above
- If the excerpts don't contain enough information, say so explicitly
- Be specific, cite which papers support each claim
- Write 150-200 words maximum
    """
    summary_prompt = PromptTemplate(template=template,
                                    validate_template=True,
                                    input_variables=['query', 'retrieved_docs'])
    summary_prompt.save(name)