"""Best-effort webpage retrieval and content extraction for ResearchPilot.

Extraction order:
1. Fetch HTML with requests and extract the main article with Trafilatura.
2. Use Beautiful Soup as a structural fallback / cleanup path.
3. If installed, retry difficult pages with Crawl4AI.
4. If installed, retry with Playwright browser rendering.

Optional dependencies are intentionally imported lazily so the API can still start
when a fallback engine has not been installed.
"""
from __future__ import annotations

import asyncio
import ipaddress
import logging
import socket
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT_SECONDS = 15
MAX_RESPONSE_BYTES = 4_000_000
MIN_USEFUL_CHARS = 350
USER_AGENT = (
    "ResearchPilot/1.0 (+research content retrieval; respects website access rules)"
)


def _is_public_http_url(url: str) -> bool:
    """Basic SSRF guard: only public HTTP(S) hosts are eligible for fetching."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return False
        host = parsed.hostname.lower()
        if host in {"localhost", "localhost.localdomain"}:
            return False
        # Reject literal IPs that are not globally routable.
        try:
            ip = ipaddress.ip_address(host)
            if not ip.is_global:
                return False
        except ValueError:
            # Resolve hostnames and reject private/local resolutions.
            try:
                addresses = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
                if not addresses:
                    return False
                for address in addresses:
                    ip = ipaddress.ip_address(address[4][0])
                    if not ip.is_global:
                        return False
            except socket.gaierror:
                return False
        return True
    except (TypeError, ValueError):
        return False


def _clean_with_bs4(html: str, base_url: str = "") -> str:
    """Structural fallback that preserves headings, links, lists and tables."""
    soup = BeautifulSoup(html, "html.parser")

    for node in soup(["script", "style", "noscript", "svg", "canvas", "iframe", "form"]):
        node.decompose()

    # Remove common non-content regions. Keep tables and main/article elements.
    for node in soup.find_all(
        ["nav", "footer", "header", "aside", "dialog"],
        limit=100,
    ):
        node.decompose()

    noise_tokens = (
        "cookie", "consent", "advert", "advertisement", "social-share",
        "share-buttons", "newsletter", "related-articles", "breadcrumb",
    )
    for node in list(soup.find_all(True)):
        attrs = " ".join(
            [str(node.get("id", "")), " ".join(node.get("class", []))]
        ).lower()
        if any(token in attrs for token in noise_tokens):
            node.decompose()

    root = soup.find("article") or soup.find("main") or soup.body or soup
    chunks = []
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    if title:
        chunks.append(f"# {title}")

    for node in root.find_all(
        ["h1", "h2", "h3", "h4", "p", "li", "blockquote", "pre", "table"],
        recursive=True,
    ):
        if node.name in {"h1", "h2", "h3", "h4"}:
            text = node.get_text(" ", strip=True)
            if text:
                level = int(node.name[1])
                chunks.append(f"{'#' * level} {text}")
        elif node.name == "table":
            rows = []
            for tr in node.find_all("tr"):
                cells = [
                    cell.get_text(" ", strip=True).replace("|", r"\|")
                    for cell in tr.find_all(["th", "td"], recursive=False)
                ]
                if cells:
                    rows.append(cells)
            if rows:
                width = max(len(row) for row in rows)
                rows = [row + [""] * (width - len(row)) for row in rows]
                chunks.append("| " + " | ".join(rows[0]) + " |")
                chunks.append("| " + " | ".join(["---"] * width) + " |")
                chunks.extend("| " + " | ".join(row) + " |" for row in rows[1:])
        else:
            text = node.get_text(" ", strip=True)
            if text:
                prefix = "- " if node.name == "li" else ""
                chunks.append(prefix + text)

    # Fallback for pages whose content is not wrapped in typical article tags.
    result = "\n\n".join(chunks).strip()
    if len(result) < MIN_USEFUL_CHARS:
        body = root.get_text("\n", strip=True)
        result = "\n\n".join([title, body]).strip()
    return result[:30_000]


def _extract_html(html: str, url: str) -> tuple[str, str]:
    """Return (content, extraction_method)."""
    try:
        import trafilatura

        extracted = trafilatura.extract(
            html,
            url=url,
            output_format="markdown",
            include_tables=True,
            include_links=True,
            include_images=False,
            include_comments=False,
            favor_precision=True,
        )
        if extracted and len(extracted.strip()) >= MIN_USEFUL_CHARS:
            return extracted.strip()[:30_000], "trafilatura"
    except ImportError:
        logger.debug("Trafilatura is not installed; using Beautiful Soup fallback.")
    except Exception:
        logger.exception("Trafilatura extraction failed for %s", url)

    return _clean_with_bs4(html, url), "beautifulsoup4"


def _fetch_http(url: str) -> tuple[str, str]:
    if not _is_public_http_url(url):
        raise ValueError("URL is not a permitted public HTTP(S) address.")

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    response = requests.get(
        url,
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
        allow_redirects=True,
        stream=True,
    )
    try:
        response.raise_for_status()
        if not _is_public_http_url(response.url):
            raise ValueError("Redirect target is not a permitted public address.")

        content_type = response.headers.get("content-type", "").lower()
        if content_type and not any(
            kind in content_type for kind in ("text/html", "application/xhtml+xml", "text/plain")
        ):
            raise ValueError(f"Unsupported content type: {content_type}")

        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=64 * 1024, decode_unicode=False):
            if not chunk:
                continue
            total += len(chunk)
            if total > MAX_RESPONSE_BYTES:
                break
            chunks.append(chunk)
        raw = b"".join(chunks)
        encoding = response.encoding or "utf-8"
        html = raw.decode(encoding, errors="replace")
        return html, response.url
    finally:
        response.close()


async def _crawl4ai_extract(url: str) -> str:
    """Optional browser-rendered fallback using Crawl4AI."""
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        wait_until="domcontentloaded",
        page_timeout=25_000,
        remove_overlay_elements=True,
        exclude_external_links=False,
    )
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)
    if not getattr(result, "success", False):
        return ""
    markdown = getattr(result, "markdown", "")
    if not isinstance(markdown, str):
        return ""
    # Current Crawl4AI versions may return a MarkdownGenerationResult object.
    if not markdown.strip() and hasattr(markdown, "raw_markdown"):
        markdown = markdown.raw_markdown
    return str(markdown).strip()[:30_000]


async def _playwright_extract(url: str) -> str:
    """Optional direct Playwright fallback for pages that need browser rendering."""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page(
                user_agent=USER_AGENT,
                java_script_enabled=True,
            )
            await page.goto(url, wait_until="domcontentloaded", timeout=25_000)
            try:
                await page.wait_for_load_state("networkidle", timeout=5_000)
            except Exception:
                pass
            html = await page.content()
            content, _ = _extract_html(html, page.url)
            return content
        finally:
            await browser.close()


def _run_async(coro):
    """Run an async fallback from the synchronous FastAPI/LangGraph pipeline."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    # The current ResearchPilot workflow is synchronous. Avoid nesting asyncio.run
    # if this function is later called from an async context.
    coro.close()
    raise RuntimeError(
        "Browser extraction was called from an active event loop; call the async "
        "extractor from an async endpoint or move this work to a worker thread."
    )


def extract_page(url: str) -> tuple[str, str]:
    """Extract a page, returning content and method; return ('', 'failed') on failure."""
    try:
        html, final_url = _fetch_http(url)
        content, method = _extract_html(html, final_url)
        if len(content.strip()) >= MIN_USEFUL_CHARS:
            return content, method
        logger.info("HTTP extraction was short for %s; trying browser fallbacks.", url)
    except Exception as exc:
        logger.info("Basic page retrieval failed for %s: %s", url, exc)

    if not _is_public_http_url(url):
        return "", "blocked"

    try:
        content = _run_async(_crawl4ai_extract(url))
        if len(content.strip()) >= MIN_USEFUL_CHARS:
            return content, "crawl4ai"
    except ImportError:
        logger.debug("Crawl4AI is not installed.")
    except Exception as exc:
        logger.info("Crawl4AI fallback failed for %s: %s", url, exc)

    try:
        content = _run_async(_playwright_extract(url))
        if len(content.strip()) >= MIN_USEFUL_CHARS:
            return content, "playwright"
    except ImportError:
        logger.debug("Playwright is not installed.")
    except Exception as exc:
        logger.info("Playwright fallback failed for %s: %s", url, exc)

    return "", "failed"
