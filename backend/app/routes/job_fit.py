from fastapi import APIRouter

from ..models.schemas import JobFitRequest, JobFitResponse
from ..services.citation_builder import build_sources
from ..services.fit_scorer import FitScorer
from ..services.job_matcher import JobMatcher
from ..services.language import detect_language
from ..services.llm import ResponseComposer
from ..services.retrieval import RetrievalService

router = APIRouter()
matcher = JobMatcher()
scorer = FitScorer()
retrieval = RetrievalService()
composer = ResponseComposer()


@router.post("", response_model=JobFitResponse)
def job_fit(payload: JobFitRequest) -> JobFitResponse:
    language = payload.language or detect_language(payload.job_description)
    match_result = matcher.match(payload.job_description)
    score = scorer.score(match_result)
    label = scorer.label(score, language)
    chunks = retrieval.search(payload.job_description)
    context = retrieval.format_context(chunks)

    summary = composer.compose_job_fit_summary(
        language,
        label,
        score,
        match_result.matched_skills,
        match_result.missing_skills,
        match_result.relevant_projects,
        context,
    )

    tips_en = [
        "Lead with projects that demonstrate matched skills.",
        "Be explicit about measurable outcomes and deployment constraints.",
    ]
    tips_fr = [
        "Mets en avant les projets qui prouvent les competences alignees.",
        "Sois precis sur les resultats et les contraintes de mise en production.",
    ]

    return JobFitResponse(
        fit_score=score,
        fit_label=label,
        summary=summary,
        matched_skills=match_result.matched_skills,
        missing_skills=match_result.missing_skills,
        relevant_projects=match_result.relevant_projects,
        positioning_tips=tips_fr if language == "fr" else tips_en,
        sources=build_sources(chunks),
    )