import os
from typing import List
from tavily import TavilyClient
from langchain_core.documents import Document
from dotenv import load_dotenv

# --------------------
# Tavily client
# --------------------
load_dotenv(override=True)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise RuntimeError("TAVILY_API_KEY not set")

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# --------------------
# Web search tool
# --------------------
def web_search_tool(query: str, max_results: int = 5) -> List[Document]:
    """
    Executes a Tavily search and returns LangChain Documents.
    This function is PURE (no side effects).
    """

    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
        include_raw_content=False
    )

    documents: List[Document] = []

    for result in response.get("results", []):
        content = result.get("content")
        if not content:
            continue

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": "web_search",
                    "tool": "tavily",
                    "url": result.get("url"),
                    "title": result.get("title"),
                    "score": result.get("score"),
                }
            )
        )

    return documents
