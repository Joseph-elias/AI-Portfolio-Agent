from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse
from app.services.citation_builder import build_sources
from app.services.language import detect_language
from app.services.llm import ResponseComposer
from app.services.retrieval import RetrievedChunk, RetrievalService

router = APIRouter()
retrieval = RetrievalService()
composer = ResponseComposer()


def _is_source_intent(msg: str) -> bool:
    m = msg.lower()
    return any(x in m for x in ["source", "sources", "evidence", "reference", "references", "proof"])


def _is_experience_intent(msg: str) -> bool:
    m = msg.lower()
    return any(x in m for x in ["experience", "work", "internship", "history", "did", "background"])


def _expand_query(message: str) -> str:
    msg = message.lower()
    expanded = message

    if _is_source_intent(msg) and _is_experience_intent(msg):
        expanded += " professional experience resume internships sissi institut curie data scientist ai engineer projects"

    if any(x in msg for x in ["backend", "api"]):
        expanded += " backend fastapi api architecture production"

    return expanded


def _source_quality_score(source: str, snippet: str, source_intent: bool, exp_intent: bool) -> float:
    s = source.lower()
    sn = snippet.lower()
    score = 0.0

    if s.startswith("resume_"):
        score += 6.0
    if s.startswith("experience/"):
        score += 5.0
    if s.startswith("projects/"):
        score += 4.0
    if s == "structured/projects.json":
        score += 2.5
    if s.startswith("bio_"):
        score += 1.5

    if s.startswith("faq"):
        score -= 20.0
    if "interests" in s or "agent_preferences" in s:
        score -= 3.0

    if source_intent and exp_intent:
        if any(x in sn for x in ["designed", "developed", "built", "implemented", "reduced", "integrated", "trained"]):
            score += 1.5
        if any(x in sn for x in ["targeting", "opportunities", "looking for", "seeking"]):
            score -= 1.5

    return score


def _refine_chunks_for_intent(chunks: list[RetrievedChunk], message: str) -> list[RetrievedChunk]:
    src_intent = _is_source_intent(message)
    exp_intent = _is_experience_intent(message)
    if not (src_intent and exp_intent):
        return chunks

    rescored = []
    for c in chunks:
        quality = _source_quality_score(c.source, c.snippet, src_intent, exp_intent)
        rescored.append(RetrievedChunk(source=c.source, snippet=c.snippet, score=c.score + quality))

    rescored.sort(key=lambda x: x.score, reverse=True)

    # keep at most one chunk per source to avoid repetitive noisy evidence blocks
    seen = set()
    selected: list[RetrievedChunk] = []
    for c in rescored:
        if c.source in seen:
            continue
        seen.add(c.source)
        selected.append(c)
        if len(selected) >= 5:
            break

    return selected if selected else rescored[:5]


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    language = payload.language or detect_language(payload.message)
    retrieval_query = _expand_query(payload.message)

    initial_k = 8 if (_is_source_intent(payload.message) and _is_experience_intent(payload.message)) else 5
    chunks = retrieval.search(retrieval_query, k=initial_k, language=language)
    chunks = _refine_chunks_for_intent(chunks, payload.message)

    context = retrieval.format_context(chunks)

    history = [{"role": h.role, "content": h.content} for h in payload.history]
    source_names = list(dict.fromkeys([c.source for c in chunks]))

    answer = composer.compose_about_answer(
        language=language,
        message=payload.message,
        snippets=[c.snippet for c in chunks],
        sources_context=context,
        history=history,
        source_names=source_names,
    )

    confidence_note = (
        "LLM answer grounded in retrieved sources." if composer.enabled else "Fallback answer grounded in retrieved sources."
    )
    if language == "fr":
        confidence_note = (
            "Reponse LLM basee sur les sources recuperees."
            if composer.enabled
            else "Reponse de secours basee sur les sources recuperees."
        )

    return ChatResponse(answer=answer, sources=build_sources(chunks), confidence_note=confidence_note)