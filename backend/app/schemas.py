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


from datetime import datetime
from pydantic import BaseModel


class ResearchHistoryItem(BaseModel):
    id: int
    question: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SavedResearchResponse(BaseModel):
    id: int
    question: str
    answer: str
    status: str
    created_at: datetime
    sources: list[Source]

    model_config = {"from_attributes": True}
