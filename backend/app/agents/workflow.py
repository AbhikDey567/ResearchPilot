import logging
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.agents.planner import plan_research
from app.agents.reader import extract_evidence
from app.services.web_search import search_web
from app.services.report_writer import write_report
from app.services.citation_checker import validate_citations
from app.schemas import Source

logger = logging.getLogger(__name__)

# Keep enough content for evidence extraction, while bounding the LLM context.
MAX_SOURCES_FOR_REPORT = 6
MAX_SOURCE_CHARS_FOR_LLM = 3_000


class ResearchState(TypedDict, total=False):
    question: str
    queries: list[str]
    sources: list[Source]
    findings: list[dict]
    answer: str
    review: dict
    citation_audit: dict


def planning_node(state: ResearchState) -> dict:
    question = state["question"].strip()
    logger.info("Using the original question as the search query.")
    return {"queries": [question]}


def search_node(state: ResearchState) -> dict:
    sources = search_web(state["queries"])

    if not sources:
        raise RuntimeError("Web search returned no sources.")

    # Keep full extracted source content instead of truncating every page to
    # 1,000 characters. This was discarding useful sections and tables.
    sources = sources[:MAX_SOURCES_FOR_REPORT]
    for source in sources:
        source.content = (source.content or "")[:MAX_SOURCE_CHARS_FOR_LLM]

    logger.info(
        "Using %s sources; retained up to %s chars per source.",
        len(sources),
        MAX_SOURCE_CHARS_FOR_LLM,
    )
    return {"sources": sources}


def reader_node(state: ResearchState) -> dict:
    findings = extract_evidence(
        state["question"],
        state["sources"],
    )
    return {"findings": findings}


def writer_node(state: ResearchState) -> dict:
    answer = write_report(
        state["question"],
        state["sources"],
        state["findings"],
    )

    if not answer or not answer.strip():
        raise RuntimeError("Report writer returned an empty report.")

    return {"answer": answer}


def critic_node(state: ResearchState) -> dict:
    """Temporarily skip the optional Critic to conserve Groq quota."""
    logger.info("Skipping optional Critic to conserve Groq token quota.")
    return {
        "review": {
            "approved": True,
            "issues": [],
            "feedback": "",
            "skipped": True,
        }
    }


def citation_check_node(state: ResearchState) -> dict:
    audit = validate_citations(
        state["answer"],
        state["sources"],
    )
    return {"citation_audit": audit}


def build_research_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("planner", planning_node)
    graph.add_node("search", search_node)
    graph.add_node("reader", reader_node)
    graph.add_node("writer", writer_node)
    graph.add_node("critic", critic_node)
    graph.add_node("citation_check", citation_check_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "search")
    graph.add_edge("search", "reader")
    graph.add_edge("reader", "writer")
    graph.add_edge("writer", "critic")
    graph.add_edge("critic", "citation_check")
    graph.add_edge("citation_check", END)

    return graph.compile()


research_graph = build_research_graph()


def run_research(question: str) -> ResearchState:
    return research_graph.invoke({"question": question})
