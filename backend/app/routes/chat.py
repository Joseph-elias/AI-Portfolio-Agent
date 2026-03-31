from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse
from app.services.citation_builder import build_sources
from app.services.consistency_engine import ConsistencyEngine
from app.services.language import detect_language
from app.services.llm import ResponseComposer
from app.services.llm_judge import LLMJudge
from app.services.retrieval import RetrievedChunk, RetrievalService

router = APIRouter()
retrieval = RetrievalService()
composer = ResponseComposer()
consistency = ConsistencyEngine()
judge = LLMJudge()


@dataclass
class ChatIntent:
    name: str
    source_intent: bool
    preferred_types: set[str] | None
    forbidden_types: set[str] | None
    k: int


def _is_source_intent(msg: str) -> bool:
    m = msg.lower()
    return any(x in m for x in ["source", "sources", "evidence", "reference", "references", "proof"])


def _classify_intent(message: str) -> ChatIntent:
    m = message.lower()
    source_intent = _is_source_intent(m)

    experience_terms = [
        "experience",
        "work",
        "internship",
        "alternance",
        "history",
        "background",
        "resume",
        "cv",
        "position",
        "job title",
        "role",
        "worked before",
    ]
    project_terms = ["project", "portfolio", "built", "build", "demo", "case study", "product"]
    skills_terms = ["skill", "stack", "tools", "backend", "frontend", "python", "fastapi", "rag", "llm"]

    if any(t in m for t in experience_terms):
        return ChatIntent(
            name="experience",
            source_intent=source_intent,
            preferred_types={"experience", "project"},
            forbidden_types={"preferences"},
            k=12 if source_intent else 10,
        )

    if any(t in m for t in project_terms):
        return ChatIntent(
            name="project",
            source_intent=source_intent,
            preferred_types={"project", "experience"},
            forbidden_types={"preferences"},
            k=10 if source_intent else 8,
        )

    if any(t in m for t in skills_terms):
        return ChatIntent(
            name="skills",
            source_intent=source_intent,
            preferred_types={"project", "experience", "profile"},
            forbidden_types={"preferences"},
            k=8,
        )

    return ChatIntent(
        name="general",
        source_intent=source_intent,
        preferred_types=None,
        forbidden_types={"preferences"},
        k=7,
    )


def _merge_planned_intent(base: ChatIntent, planned_intent: str) -> ChatIntent:
    if planned_intent in {"experience", "skills", "project", "general"}:
        return ChatIntent(
            name=planned_intent,
            source_intent=base.source_intent,
            preferred_types=base.preferred_types,
            forbidden_types=base.forbidden_types,
            k=base.k,
        )

    # Map richer planner intents to retrieval-friendly buckets.
    if planned_intent in {"internship_experience", "publications"}:
        return ChatIntent(
            name="experience",
            source_intent=base.source_intent,
            preferred_types={"experience", "project"},
            forbidden_types={"preferences"},
            k=max(base.k, 10),
        )

    if planned_intent in {"self_intro", "education", "contract", "hire"}:
        return ChatIntent(
            name="general",
            source_intent=base.source_intent,
            preferred_types={"experience", "project", "profile", "certification"},
            forbidden_types={"preferences"},
            k=max(base.k, 8),
        )

    return base


def _expand_query(message: str, intent: ChatIntent) -> str:
    expanded = message

    if intent.name == "experience":
        expanded += " work experience employment history positions role title company internship alternance stage m1 apprenticeship cv resume institut curie inserm lifex publication manuscript dates sissi co-founder ai engineer current present startup saas"
    elif intent.name == "project":
        expanded += " projects products shipped implemented architecture outcomes"
    elif intent.name == "skills":
        expanded += " technical stack skills frameworks tools backend frontend rag llm"

    if intent.source_intent:
        expanded += " include source evidence references"

    return expanded


def _rerank_chunks(chunks: list[RetrievedChunk], message: str, intent: ChatIntent) -> list[RetrievedChunk]:
    rescored: list[RetrievedChunk] = []

    for chunk in chunks:
        score = chunk.score
        s = chunk.source.lower()
        sn = chunk.snippet.lower()

        if intent.name == "experience":
            if chunk.chunk_type == "experience":
                score += 3.0
            if any(x in sn for x in ["intern", "alternance", "co-founder", "engineer", "curie", "startup"]):
                score += 1.7
            if any(x in sn for x in ["sissi", "co-founder", "ai engineer", "executive assistant startup", "01/2026", "present"]):
                score += 2.4
            if any(x in sn for x in ["targeting", "seeking", "looking for"]):
                score -= 1.8
            if any(x in sn for x in ["202", "201", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]):
                score += 1.0

        if intent.name == "project":
            if chunk.chunk_type == "project":
                score += 2.6
            if any(x in sn for x in ["built", "implemented", "deployed", "pipeline", "api"]):
                score += 1.2

        if intent.name == "skills":
            if any(x in sn for x in ["python", "fastapi", "rag", "llm", "next.js", "api"]):
                score += 1.4

        if intent.source_intent and chunk.chunk_type in {"experience", "project", "certification"}:
            score += 0.8

        if "agent_preferences" in s or "interests" in s or s.startswith("faq"):
            score -= 4.5

        rescored.append(
            RetrievedChunk(source=chunk.source, snippet=chunk.snippet, score=score, chunk_type=chunk.chunk_type)
        )

    rescored.sort(key=lambda c: c.score, reverse=True)

    selected: list[RetrievedChunk] = []
    per_source_count: dict[str, int] = {}

    if intent.name == "experience":
        limit = 9
        max_per_source = 3
    else:
        limit = 6
        max_per_source = 1

    for chunk in rescored:
        count = per_source_count.get(chunk.source, 0)
        if count >= max_per_source:
            continue
        per_source_count[chunk.source] = count + 1
        selected.append(chunk)
        if len(selected) >= limit:
            break

    return selected if selected else rescored[:limit]


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    language = payload.language or detect_language(payload.message)

    plan = consistency.plan(payload.message)
    normalized_message = plan.normalized_message

    intent = _classify_intent(normalized_message)
    intent = _merge_planned_intent(intent, plan.intent)
    retrieval_query = _expand_query(normalized_message, intent)

    chunks = retrieval.search(
        retrieval_query,
        k=intent.k,
        language=language,
        preferred_types=intent.preferred_types,
        forbidden_types=intent.forbidden_types,
    )

    chunks = _rerank_chunks(chunks, normalized_message, intent)
    if not chunks:
        chunks = retrieval.search(normalized_message, k=5, language=language, forbidden_types={"preferences"})

    context = retrieval.format_context(chunks)

    history = [{"role": h.role, "content": h.content} for h in payload.history]
    source_names = list(dict.fromkeys([c.source for c in chunks]))

    deterministic = consistency.deterministic_answer(plan, language)
    if deterministic:
        answer = deterministic
    else:
        answer = composer.compose_about_answer(
            language=language,
            message=normalized_message,
            snippets=[c.snippet for c in chunks],
            sources_context=context,
            history=history,
            source_names=source_names,
            intent=intent.name,
        )

    if not consistency.validate_answer(answer, plan):
        answer = consistency.repair_answer(plan, language, answer)

    judge_result = judge.review(
        message=normalized_message,
        answer=answer,
        language=language,
        plan_intent=plan.intent,
        required_keywords=plan.required_keywords_en,
        sources_context=context,
    )
    if judge_result.revised_answer:
        answer = judge_result.revised_answer

    confidence_note = (
        "LLM answer grounded in retrieved sources." if composer.enabled else "Fallback answer grounded in retrieved sources."
    )
    if deterministic:
        confidence_note = "Deterministic truth-profile answer with retrieval support."
    elif judge_result.checked:
        confidence_note += " LLM judge checked for consistency."

    if language == "fr":
        confidence_note = (
            "Reponse LLM basee sur les sources recuperees."
            if composer.enabled
            else "Reponse de secours basee sur les sources recuperees."
        )
        if deterministic:
            confidence_note = "Reponse deterministe basee sur le profil de verite et appuyee par la recuperation."
        elif judge_result.checked:
            confidence_note += " Verification LLM judge effectuee pour la coherence."

    return ChatResponse(answer=answer, sources=build_sources(chunks), confidence_note=confidence_note)
