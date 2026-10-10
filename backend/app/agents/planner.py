
import json
import logging

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import GROQ_API_KEY, GROQ_MODEL


logger = logging.getLogger(__name__)

MAX_QUERIES = 4


def plan_research(question: str) -> list[str]:
    """Turn a research question into focused web-search queries."""

    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    llm = ChatGroq(
        model=GROQ_MODEL,
        temperature=0.1,
        max_retries=1,
        timeout=30,
    )

    response = llm.invoke([
        SystemMessage(
            content=(
                "You are the research planner for ResearchPilot. "
                "Break the user's research question into 2 to 4 distinct, "
                "useful web-search queries. Cover different aspects of "
                "the question, avoid duplicate queries, and preserve "
                "important names, dates, and comparison criteria. "
                "For a simple factual question, use one focused query. "
                "Return ONLY a valid JSON array of strings. "
                "Do not include Markdown fences or commentary."
            )
        ),
        HumanMessage(
            content=f"Research question:\n{question}"
        ),
    ])

    raw = str(response.content).strip()

    # Handle accidental Markdown code fences.
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw[:-3].strip()

    try:
        queries = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Planner returned invalid JSON; using original question.")
        return [question]

    if not isinstance(queries, list):
        return [question]

    cleaned = []
    for query in queries:
        if isinstance(query, str):
            query = query.strip()
            if query and query not in cleaned:
                cleaned.append(query)

        if len(cleaned) >= MAX_QUERIES:
            break

    return cleaned or [question]
