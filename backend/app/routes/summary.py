from fastapi import APIRouter

from app.models.schemas import ProfileSummaryResponse
from app.services.profile_loader import ProfileLoader

router = APIRouter()
loader = ProfileLoader()


@router.get("", response_model=ProfileSummaryResponse)
def summary() -> ProfileSummaryResponse:
    projects = [p.get("name", "Unnamed project") for p in loader.projects][:3]
    roles = loader.preferences.get("target_roles", [])[:4]
    spoken = loader.skills.get("spoken_languages", [])

    return ProfileSummaryResponse(
        intro_30s="Bilingual AI builder focused on RAG, APIs, and product-oriented engineering.",
        top_strengths=["RAG systems", "FastAPI backends", "Applied LLM workflows"],
        relevant_projects=projects,
        preferred_roles=roles,
        spoken_languages=spoken,
        tech_stack_summary="Python, FastAPI, Next.js, vector search, prompt engineering",
    )
