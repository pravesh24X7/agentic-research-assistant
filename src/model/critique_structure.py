from pydantic import BaseModel, Field


class CritiqueStructure(BaseModel):
    critique_score: float = Field(default=1, gt=0, lt=11, description="Overall score of the generated answer.")
    critique: str = Field(description="Textual report of the generated answer.")