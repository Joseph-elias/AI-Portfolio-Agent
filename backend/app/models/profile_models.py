from pydantic import BaseModel


class CandidateProject(BaseModel):
    name: str
    domains: list[str]
    skills_used: list[str]
    summary_en: str
    summary_fr: str
