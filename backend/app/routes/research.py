import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.workflow import run_research
from app.config import TAVILY_API_KEY, GROQ_API_KEY
from app.database import get_db
from app.models import ResearchJob, Source as SourceModel, ResearchFinding
from app.schemas import ResearchRequest, ResearchResponse
from app.models import ResearchJob
from app.schemas import ResearchHistoryItem, SavedResearchResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "application": "ResearchPilot",
    }


@router.post("/research", response_model=ResearchResponse)
def research(
    request: ResearchRequest,
    db: Session = Depends(get_db),
):
    question = request.question.strip()

    if len(question) < 3:
        raise HTTPException(
            status_code=422,
            detail="Please enter a meaningful research question.",
        )

    if not TAVILY_API_KEY or not GROQ_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Configure TAVILY_API_KEY and GROQ_API_KEY in backend/.env",
        )

    try:
        logger.info("Starting LangGraph research workflow.")

        result = run_research(question)

        # Extract the completed workflow result before persisting it.
        answer = result["answer"]
        sources = result["sources"]
        findings = result.get("findings", [])
        citation_audit = result.get("citation_audit", {})

        # Save the report and related records atomically.
        try:
            job = ResearchJob(
                question=question,
                status="completed",
                answer=answer,
            )

            db.add(job)
            db.flush()

            for source in sources:
                db.add(
                    SourceModel(
                        research_id=job.id,
                        title=source.title,
                        url=source.url,
                        content=source.content,
                    )
                )

            for finding in findings:
                db.add(
                    ResearchFinding(
                        research_id=job.id,
                        source_id=finding.get("source_id"),
                        finding=finding.get("finding", ""),
                        evidence=finding.get("evidence", ""),
                        caveat=finding.get("caveat", ""),
                    )
                )

            db.commit()
            logger.info("Saved research job %s to SQLite.", job.id)

        except Exception as exc:
            db.rollback()
            logger.exception("Failed to persist research results.")
            raise HTTPException(
                status_code=500,
                detail="The report was generated but could not be saved.",
            ) from exc

        logger.info(
            "Research completed with %s sources.",
            len(sources),
        )

        if citation_audit.get("invalid_citations"):
            logger.warning(
                "Citation audit found invalid references: %s",
                citation_audit["invalid_citations"],
            )

        return ResearchResponse(
            question=question,
            answer=answer,
            sources=sources,
        )

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Research workflow failed.")

        raise HTTPException(
            status_code=502,
            detail=(
                "Research could not be completed. Check the backend logs "
                "and API provider status, then try again."
            ),
        ) from exc


@router.get("/research/history", response_model=list[ResearchHistoryItem])
def get_research_history(db: Session = Depends(get_db)):
    jobs = db.query(ResearchJob).order_by(ResearchJob.created_at.desc()).all()

    return jobs


@router.get(
    "/research/history/{job_id}",
    response_model=SavedResearchResponse,
)
def get_saved_research(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = db.query(ResearchJob).filter(ResearchJob.id == job_id).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Research report not found.",
        )

    return {
        "id": job.id,
        "question": job.question,
        "answer": job.answer or "",
        "status": job.status,
        "created_at": job.created_at,
        "sources": [
            {
                "title": source.title,
                "url": source.url,
                "content": source.content,
            }
            for source in job.sources
        ],
    }


@router.delete("/research/history/{job_id}")
def delete_saved_research(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = db.query(ResearchJob).filter(ResearchJob.id == job_id).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Research report not found.",
        )

    db.delete(job)
    db.commit()

    return {
        "message": "Research report deleted successfully.",
        "id": job_id,
    }
