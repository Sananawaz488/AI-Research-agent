"""
A simple, free web search tool for our CrewAI agent, built on the
`ddgs` package (the current, maintained version of the old
`duckduckgo_search` package - no API key required).
"""

from crewai.tools import BaseTool
from ddgs import DDGS


class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGo Search"
    description: str = (
        "Searches the web using DuckDuckGo for a given query and returns "
        "the top results (title, short snippet, and link). Use this "
        "whenever you need current, real-world information on a topic."
    )

    def _run(self, query: str) -> str:
        try:
            results = DDGS().text(query, max_results=5)
        except Exception as exc:
            return f"Search failed for query '{query}': {exc}"

        if not results:
            return f"No results found for query: '{query}'"

        formatted = []
        for i, r in enumerate(results, start=1):
            title = r.get("title", "No title")
            snippet = r.get("body", "No description")
            link = r.get("href", "No link")
            formatted.append(f"{i}. {title}\n{snippet}\nSource: {link}\n")

        return "\n".join(formatted)
