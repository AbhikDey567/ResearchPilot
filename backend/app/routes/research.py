from app.agents.planner import plan_research
from app.agents.reader import extract_evidence
from app.agents.critic import review_report
import logging

from fastapi import APIRouter, HTTPException

from app.config import TAVILY_API_KEY, GROQ_API_KEY
from app.schemas import ResearchRequest, ResearchResponse
from app.services.web_search import search_web
from app.services.report_writer import write_report, revise_report

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "application": "ResearchPilot",
    }


@router.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest):
    if not TAVILY_API_KEY or not GROQ_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Configure TAVILY_API_KEY and GROQ_API_KEY in backend/.env",
        )

    question = request.question.strip()

    if len(question) < 3:
        raise HTTPException(
            status_code=422,
            detail="Please enter a meaningful research question.",
        )

    try:

        queries = plan_research(question)
        sources = search_web(queries)
        findings = extract_evidence(question, sources)
        answer = write_report(question, sources, findings)

        # One quality review, followed by at most one revision.
        try:
            review = review_report(question, answer, findings)

            if not review["approved"] and review["feedback"].strip():
                logger.info("Critic requested a report revision.")

                try:
                    answer = revise_report(
                        question,
                        answer,
                        findings,
                        review["feedback"],
                    )
                except Exception:
                    logger.exception(
                        "Report revision failed; preserving the original draft."
                    )

        except Exception:
            logger.exception("Critic review failed; preserving the original draft.")

        return ResearchResponse(
            question=question,
            answer=answer,
            sources=sources,
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception("Research request failed")

        raise HTTPException(
            status_code=502,
            detail=(
                "Research could not be completed. Check the backend logs "
                "and API provider status, then try again."
            ),
        )
