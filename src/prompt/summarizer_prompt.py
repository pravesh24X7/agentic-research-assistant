from langchain_core.prompts import PromptTemplate


def create_summary_prompt(name: str):

    template = """
You are an expert research assistant.

Answer the user's question ONLY using the supplied research context.

Question:
{query}


Retrieved Context:
{retrieved_docs}


Available Citation Metadata:
{citation_info}


Rules:

1. Use ONLY information found in the retrieved context.

2. Do NOT use prior knowledge.

3. If context is insufficient, explicitly state:
   "The provided documents do not contain sufficient information."

4. Every factual claim MUST include citations.

5. Citation format:

   [source,page]

Examples:

CNN achieved 98.4% accuracy
[blood_group.pdf,p12]

Transformer-based methods improved classification performance
[paper1.pdf,p8][paper2.pdf,p15]

6. If multiple sources support the same statement,
include multiple citations.

7. Prefer uploaded documents over generic abstracts
when both contain relevant information.

8. Mention model names, metrics, datasets,
and experimental findings whenever available.

9. Keep the answer concise but informative
(150–250 words).

10. Never invent page numbers or sources.


Answer:
"""

    summary_prompt = PromptTemplate(
        template=template,
        validate_template=True,
        input_variables=[
            "query",
            "retrieved_docs",
            "citation_info"
        ]
    )

    summary_prompt.save(name)