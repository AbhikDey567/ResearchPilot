import logging
from urllib.parse import urlparse

from fastapi import HTTPException
from tavily import TavilyClient

from app.config import TAVILY_API_KEY
from app.schemas import Source
from app.services.content_extractor import extract_page

logger = logging.getLogger(__name__)

MAX_RESULTS_PER_QUERY = 3
MAX_TOTAL_SOURCES = 8
MAX_SOURCE_CHARS = 12_000


def _is_http_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname)
    except ValueError:
        return False


def search_web(queries: list[str]) -> list[Source]:
    """Search with Tavily, then enrich snippets with extracted page content.

    Tavily's content is retained as a fallback when direct extraction is blocked,
    unavailable, or shorter than the search result snippet.
    """
    if not TAVILY_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Configure TAVILY_API_KEY in backend/.env",
        )

    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    collected_sources: list[Source] = []
    seen_urls: set[str] = set()

    for query in queries:
        try:
            search_result = tavily.search(
                query=query,
                search_depth="advanced",
                max_results=MAX_RESULTS_PER_QUERY,
                topic="general",
                include_raw_content=True,
            )
        except TypeError:
            # Compatibility with Tavily SDK versions that don't accept
            # include_raw_content.
            try:
                search_result = tavily.search(
                    query=query,
                    search_depth="advanced",
                    max_results=MAX_RESULTS_PER_QUERY,
                    topic="general",
                )
            except Exception:
                logger.warning("A web search failed for one planned query.", exc_info=True)
                continue
        except Exception:
            logger.warning("A web search failed for one planned query.", exc_info=True)
            continue

        for item in search_result.get("results", []):
            url = item.get("url")
            if not isinstance(url, str) or not _is_http_url(url):
                continue

            normalized_url = url.rstrip("/").lower()
            if normalized_url in seen_urls:
                continue
            seen_urls.add(normalized_url)

            # Prefer Tavily's raw content when it is available; otherwise use
            # its snippet until direct extraction succeeds.
            tavily_content = (
                item.get("raw_content")
                or item.get("content")
                or ""
            ).strip()[:MAX_SOURCE_CHARS]
            content = tavily_content
            extraction_method = "tavily"

            try:
                extracted, method = extract_page(url)
                if extracted and (
                    len(extracted) > len(content)
                    or len(content) < 500
                ):
                    content = extracted[:MAX_SOURCE_CHARS]
                    extraction_method = method
            except Exception:
                logger.warning("Page extraction failed for %s; retaining Tavily content.", url, exc_info=True)

            if not content:
                content = "No readable page content could be extracted. Use the source URL for manual verification."

            # Source currently has title/url/content fields. Keep extraction
            # metadata inside content-independent logs to avoid schema changes.
            logger.info(
                "Source retrieved: method=%s chars=%s url=%s",
                extraction_method,
                len(content),
                url,
            )
            collected_sources.append(
                Source(
                    title=item.get("title") or "Untitled source",
                    url=url,
                    content=content,
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
