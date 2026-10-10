
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.research import router as research_router


app = FastAPI(
    title="ResearchPilot API",
    description="Web research API for ResearchPilot",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(research_router, prefix="/api")
