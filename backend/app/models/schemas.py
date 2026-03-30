from typing import Literal

from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    source: str
    snippet: str


class ChatTurn(BaseModel):
    role: Literal["assistant", "user"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    language: Literal["en", "fr"] | None = None
    history: list[ChatTurn] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    confidence_note: str


class JobFitRequest(BaseModel):
    job_description: str = Field(min_length=1)
    language: Literal["en", "fr"] | None = None


class JobFitResponse(BaseModel):
    fit_score: int
    fit_label: str
    summary: str
    matched_skills: list[str]
    missing_skills: list[str]
    relevant_projects: list[str]
    positioning_tips: list[str]
    sources: list[SourceItem]


class ProfileSummaryResponse(BaseModel):
    intro_30s: str
    top_strengths: list[str]
    relevant_projects: list[str]
    preferred_roles: list[str]
    spoken_languages: list[str]
    tech_stack_summary: str