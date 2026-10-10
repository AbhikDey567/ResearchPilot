
import logging

from fastapi import HTTPException
from tavily import TavilyClient

from app.config import TAVILY_API_KEY
from app.schemas import Source


logger = logging.getLogger(__name__)

MAX_RESULTS_PER_QUERY = 3
MAX_TOTAL_SOURCES = 8


def search_web(queries: list[str]) -> list[Source]:
    """Search multiple queries and return deduplicated sources."""

    if not TAVILY_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Configure TAVILY_API_KEY in backend/.env",
        )

    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    collected_sources = []
    seen_urls = set()

    for query in queries:
        try:
            search_result = tavily.search(
                query=query,
                search_depth="basic",
                max_results=MAX_RESULTS_PER_QUERY,
                topic="general",
            )
        except Exception as exc:
            logger.warning("A web search failed for one planned query.")
            continue

        for item in search_result.get("results", []):
            url = item.get("url")

            if not isinstance(url, str):
                continue

            if not url.startswith(("https://", "http://")):
                continue

            normalized_url = url.rstrip("/").lower()

            if normalized_url in seen_urls:
                continue

            seen_urls.add(normalized_url)

            collected_sources.append(
                Source(
                    title=item.get("title") or "Untitled source",
                    url=url,
                    content=(item.get("content") or "")[:5000],
                )
            )

            if len(collected_sources) >= MAX_TOTAL_SOURCES:
                return collected_sources

    if not collected_sources:
        raise HTTPException(
            status_code=502,
            detail="No useful search results were returned. Try another question.",
        )

    return collected_sources
