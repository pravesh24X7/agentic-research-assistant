from pydantic import BaseModel, Field


class SearchStructure(BaseModel):
    search_query: str = Field(description="words or sentence you type into a search engine or search box to find information.")

