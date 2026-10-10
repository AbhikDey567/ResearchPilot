
from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class Source(BaseModel):
    title: str
    url: str
    content: str


class ResearchResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]
