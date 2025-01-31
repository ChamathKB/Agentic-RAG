from langchain.tools.tavily_search import TavilySearchResults
from langchain.utilities.tavily_search import TavilySearchAPIWrapper

from app.configs import TAVILY_API_KEY


def search() -> TavilySearchResults:
    """
    Creates and returns a TavilySearchResults tool for performing web searches.

    Returns:
        TavilySearchResults: A search tool configured with the Tavily API wrapper
    """
    search = TavilySearchAPIWrapper(tavily_api_key=TAVILY_API_KEY)
    search_tool = TavilySearchResults(api_wrapper=search)
    return search_tool
