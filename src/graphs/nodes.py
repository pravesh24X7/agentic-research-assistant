import json
from langchain_core.prompts import load_prompt
from langchain_core.output_parsers import PydanticOutputParser

from src.rag.retriever import get_retriever
from src.graphs.state import AgentState
from src.model.execution_chain import chain
from src.model.chat_model import llm_model
from src.model.cirtique_structure import CritiqueStructure
from src.config.settings import SAVE_PROMPT_TO


def retriever(state: AgentState) -> dict:
    retriever = get_retriever()
    result = retriever.invoke(state['query'])
    return {
        'retrieved_docs': [ doc.page_content for doc in result ]
    }
    
    

def summary(state: AgentState) -> dict:
    execution_chain = chain(f'{SAVE_PROMPT_TO}/summary_prompt.json')

    result = execution_chain.invoke({
        "query": state['query'],
        "retrieved_docs": state["retrieved_docs"]
    })

    return {
        'draft_answer': [result],
        'iterations': state['iterations'] + 1
    }
    


def critique(state: AgentState) -> dict:
    prompt = load_prompt(f'{SAVE_PROMPT_TO}/critique_prompt.json')

    parser = PydanticOutputParser(pydantic_object=CritiqueStructure)

    structured_llm = llm_model()
    execution_chain = prompt | structured_llm | parser

    result = execution_chain.invoke({
        'query': state['query'],
        'draft_answer': state['draft_answer'][-1],
        'instructions': parser.get_format_instructions(),
    })
    
    return {
        'critique_score': result.critique_score,
        'critique': result.critique
    }


def synthesiser(state: AgentState) -> dict:

    execution_chain = chain(f'{SAVE_PROMPT_TO}/synthesiser_prompt.json')

    result = execution_chain.invoke({
        'query': state['query'],
        'draft_answer': state['draft_answer'][-1],
        'critique': state['critique']
    })

    return {
        'draft_answer': [result],
        'iterations': state['iterations'] + 1,
    }


def generate_final_answer(state: AgentState) -> dict:

    execution_chain = chain(f'{SAVE_PROMPT_TO}/base_prompt.json')

    query = f"""
You are an expert scientific analyst tasked with producing a comprehensive, rigorous report. Below is the context for your analysis:

Context: {state['retrieved_docs']}
phrase: {state['draft_answer'][-1]}

Your job:
1. Carefully analyze the provided context and extract all relevant information.
2. Use appropriate scientific reasoning and, if necessary, **mathematical notations, formulas, or derivations**.
3. If helpful, create **visualizations**, **tables**, or **diagrams** to clarify relationships or results.
4. Identify any gaps, inconsistencies, or assumptions in the context.
5. Summarize intermediate findings clearly and logically.
6. Integrate all information into a **final, well-supported answer** to the question.

Requirements:
- Be thorough and precise; assume the audience is a knowledgeable expert.
- When using mathematics, ensure equations are correctly formatted and labeled.
- Tables or visualizations should have clear titles, labels, and units if applicable.
- The final answer should be concise, definitive, and clearly highlighted at the end under "Final Answer".

Output Format:
1. Analysis and Reasoning: Provide step-by-step analysis and discussion.
2. Optional Visualizations/Tables: Include any figures, plots, or tables that aid understanding.
3. Final Answer: Clearly state the final conclusion or solution.
"""

    result = execution_chain.invoke({
        'query': query
    })

    return {
        'final_answer': result
    }