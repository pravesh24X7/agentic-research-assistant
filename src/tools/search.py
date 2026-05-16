from langchain_core.tools import StructuredTool
from langchain_community.tools.tavily_search import TavilySearchResults
from src.tools.structure import SearchStructure


def search_engine(search_query: str) -> str:
    """
    Takes search query and returns the answers after searching them on web.
    """

    search_tool = TavilySearchResults(max_results=10)
    results = search_tool.invoke({
        'query': search_query
    })

    return "\n\n".join([ content["content"] for content in results ])

search_tool = StructuredTool.from_function(
    func=search_engine,
    args_schema=SearchStructure,
    description="Search engine tool to perform online searches of given search query",
    name="search_tool"
)