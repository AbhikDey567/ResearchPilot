
from fastapi import HTTPException
from tavily import TavilyClient

from app.config import TAVILY_API_KEY
from app.schemas import Source


def search_web(question: str) -> list[Source]:
    if not TAVILY_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Configure TAVILY_API_KEY in backend/.env",
        )

    try:
        tavily = TavilyClient(api_key=TAVILY_API_KEY)

        search_result = tavily.search(
            query=question,
            search_depth="basic",
            max_results=5,
            topic="general",
        )
    except Exception as exc:
        raise RuntimeError("Web search failed.") from exc

    results = search_result.get("results", [])

    if not results:
        raise HTTPException(
            status_code=502,
            detail="No useful search results were returned. Try another question.",
        )

    sources = [
        Source(
            title=item.get("title") or "Untitled source",
            url=item["url"],
            content=(item.get("content") or "")[:5000],
        )
        for item in results
        if isinstance(item.get("url"), str)
        and item["url"].startswith(("https://", "http://"))
    ]

    if not sources:
        raise HTTPException(
            status_code=502,
            detail="Search results did not contain usable source URLs.",
        )

    return sources
