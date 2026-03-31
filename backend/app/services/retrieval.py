from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass

from ..core.config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL, TOP_K, USE_OPENAI, VECTOR_STORE_DIR
from .profile_loader import ProfileLoader

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


@dataclass
class RetrievedChunk:
    source: str
    snippet: str
    score: float
    chunk_type: str


class RetrievalService:
    def __init__(self) -> None:
        self.loader = ProfileLoader()
        self._chunks = self._build_chunks()
        self.client = OpenAI(api_key=OPENAI_API_KEY) if (USE_OPENAI and OpenAI is not None) else None
        self._embedding_cache_path = VECTOR_STORE_DIR / "embedding_cache.json"
        self._embedding_cache = self._load_cache()

    @staticmethod
    def _clean_text_block(text: str) -> str:
        cleaned_lines = []
        for line in text.splitlines():
            line = re.sub(r"^\s*#+\s*", "", line)
            line = re.sub(r"^\s*[-*]\s+", "", line)
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        return "\n".join(cleaned_lines).strip()

    @staticmethod
    def _infer_chunk_type(source: str) -> str:
        s = source.lower()
        if s.startswith("experience/") or s.startswith("resume_") or s.endswith(".pdf"):
            return "experience"
        if s.startswith("projects/") or s == "structured/projects.json":
            return "project"
        if "certification" in s:
            return "certification"
        if any(x in s for x in ["agent_preferences", "interests", "faq"]):
            return "preferences"
        return "profile"

    @staticmethod
    def _split_for_chunks(text: str, size: int = 650, overlap: int = 120) -> list[str]:
        if len(text) <= size:
            return [text]
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + size, len(text))
            piece = text[start:end].strip()
            if piece:
                chunks.append(piece)
            if end >= len(text):
                break
            start = max(end - overlap, start + 1)
        return chunks

    def _build_chunks(self) -> list[RetrievedChunk]:
        chunks: list[RetrievedChunk] = []
        for source, text in self.loader.all_raw_docs():
            cleaned = self._clean_text_block(text)
            if not cleaned:
                continue
            chunk_type = self._infer_chunk_type(source)
            parts = [x.strip() for x in cleaned.split("\n\n") if x.strip()]
            for part in parts:
                for piece in self._split_for_chunks(part, size=650, overlap=120):
                    chunks.append(RetrievedChunk(source=source, snippet=piece, score=0.0, chunk_type=chunk_type))

        for project in self.loader.projects:
            name = project.get("name", "Unnamed project")
            summary_en = project.get("summary_en", "")
            summary_fr = project.get("summary_fr", "")
            skills = ", ".join(project.get("skills_used", []))
            payload = f"{name}. {summary_en} {summary_fr} Skills used: {skills}".strip()
            chunks.append(
                RetrievedChunk(source="structured/projects.json", snippet=payload[:650], score=0.0, chunk_type="project")
            )
        return chunks

    @staticmethod
    def _source_matches_language(source: str, language: str | None) -> bool:
        if language is None:
            return True
        if source.endswith("_en.md"):
            return language == "en"
        if source.endswith("_fr.md"):
            return language == "fr"
        return True

    @staticmethod
    def _source_intent_boost(source: str, query: str, chunk_type: str) -> float:
        q = query.lower()
        s = source.lower()
        boost = 0.0

        if chunk_type == "preferences":
            boost -= 3.5

        if any(x in q for x in ["experience", "work", "internship", "alternance", "history", "resume", "cv", "role", "position"]):
            if chunk_type == "experience":
                boost += 4.0
            if chunk_type == "project":
                boost += 1.8

        if any(x in q for x in ["project", "portfolio", "built", "build", "demo"]):
            if chunk_type == "project":
                boost += 3.2
            if chunk_type == "experience":
                boost += 1.0

        if any(x in q for x in ["source", "sources", "evidence", "reference", "proof"]):
            if chunk_type in {"experience", "project", "certification"}:
                boost += 1.5

        if any(x in q for x in ["backend", "api", "fastapi"]):
            if chunk_type in {"project", "experience"}:
                boost += 1.8

        if any(x in s for x in ["agent_preferences", "interests", "faq"]):
            boost -= 2.0

        return boost

    def _load_cache(self) -> dict[str, list[float]]:
        VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
        if not self._embedding_cache_path.exists():
            return {}
        try:
            return json.loads(self._embedding_cache_path.read_text(encoding="utf-8-sig"))
        except Exception:
            return {}

    def _save_cache(self) -> None:
        self._embedding_cache_path.write_text(json.dumps(self._embedding_cache), encoding="utf-8")

    @staticmethod
    def _dot(a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    @staticmethod
    def _norm(a: list[float]) -> float:
        return math.sqrt(sum(x * x for x in a))

    def _embedding(self, text: str) -> list[float] | None:
        key = text[:1000]
        if key in self._embedding_cache:
            return self._embedding_cache[key]
        if self.client is None:
            return None

        try:
            emb = self.client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=text)
            vector = emb.data[0].embedding
            self._embedding_cache[key] = vector
            self._save_cache()
            return vector
        except Exception:
            return None

    @staticmethod
    def _type_allowed(chunk: RetrievedChunk, preferred_types: set[str] | None, forbidden_types: set[str] | None) -> bool:
        if forbidden_types and chunk.chunk_type in forbidden_types:
            return False
        if preferred_types is None:
            return True
        return chunk.chunk_type in preferred_types

    @staticmethod
    def _keyword_overlap_score(text: str, query_terms: list[str]) -> float:
        return float(sum(1 for t in query_terms if t in text))

    def _keyword_search(
        self,
        query: str,
        k: int,
        language: str | None,
        preferred_types: set[str] | None,
        forbidden_types: set[str] | None,
    ) -> list[RetrievedChunk]:
        q_terms = [t for t in query.lower().split() if len(t) > 2]
        scored: list[RetrievedChunk] = []

        for c in self._chunks:
            if not self._source_matches_language(c.source, language):
                continue
            if not self._type_allowed(c, preferred_types, forbidden_types):
                continue
            text = c.snippet.lower()
            base = self._keyword_overlap_score(text, q_terms)
            if base > 0:
                score = base + self._source_intent_boost(c.source, query, c.chunk_type)
                scored.append(RetrievedChunk(source=c.source, snippet=c.snippet, score=score, chunk_type=c.chunk_type))

        scored.sort(key=lambda x: x.score, reverse=True)
        if scored:
            return scored[:k]

        fallback = [
            c
            for c in self._chunks
            if self._source_matches_language(c.source, language)
            and self._type_allowed(c, None, forbidden_types)
        ]
        return fallback[:k] if fallback else self._chunks[:k]

    def _semantic_scores(
        self,
        query: str,
        language: str | None,
        preferred_types: set[str] | None,
        forbidden_types: set[str] | None,
    ) -> dict[int, float]:
        query_vector = self._embedding(query)
        if query_vector is None:
            return {}

        qn = self._norm(query_vector) or 1.0
        semantic: dict[int, float] = {}

        for idx, c in enumerate(self._chunks):
            if not self._source_matches_language(c.source, language):
                continue
            if not self._type_allowed(c, preferred_types, forbidden_types):
                continue
            cv = self._embedding(c.snippet)
            if cv is None:
                continue
            denom = (self._norm(cv) * qn) or 1.0
            similarity = self._dot(query_vector, cv) / denom
            semantic[idx] = similarity

        return semantic

    def _keyword_scores(
        self,
        query: str,
        language: str | None,
        preferred_types: set[str] | None,
        forbidden_types: set[str] | None,
    ) -> dict[int, float]:
        q_terms = [t for t in query.lower().split() if len(t) > 2]
        keyword: dict[int, float] = {}

        for idx, c in enumerate(self._chunks):
            if not self._source_matches_language(c.source, language):
                continue
            if not self._type_allowed(c, preferred_types, forbidden_types):
                continue
            base = self._keyword_overlap_score(c.snippet.lower(), q_terms)
            if base > 0:
                keyword[idx] = base

        return keyword

    def _fused_search(
        self,
        query: str,
        k: int,
        language: str | None,
        preferred_types: set[str] | None,
        forbidden_types: set[str] | None,
    ) -> list[RetrievedChunk]:
        semantic = self._semantic_scores(query, language, preferred_types, forbidden_types)
        keyword = self._keyword_scores(query, language, preferred_types, forbidden_types)

        # if semantic is unavailable, keep existing keyword behavior
        if not semantic:
            return self._keyword_search(query, k, language, preferred_types, forbidden_types)

        # Normalize both channels and fuse
        fused: dict[int, float] = {}
        max_sem = max(semantic.values()) if semantic else 1.0
        max_kw = max(keyword.values()) if keyword else 1.0
        max_sem = max_sem if max_sem > 0 else 1.0
        max_kw = max_kw if max_kw > 0 else 1.0

        candidate_ids = set(semantic.keys()) | set(keyword.keys())
        for idx in candidate_ids:
            s_norm = semantic.get(idx, 0.0) / max_sem
            k_norm = keyword.get(idx, 0.0) / max_kw
            chunk = self._chunks[idx]
            fused_score = (0.72 * s_norm) + (0.28 * k_norm)
            fused_score += self._source_intent_boost(chunk.source, query, chunk.chunk_type)
            fused[idx] = fused_score

        ranked_ids = sorted(fused.keys(), key=lambda i: fused[i], reverse=True)
        results: list[RetrievedChunk] = []
        for idx in ranked_ids[:k]:
            chunk = self._chunks[idx]
            results.append(
                RetrievedChunk(
                    source=chunk.source,
                    snippet=chunk.snippet,
                    score=fused[idx],
                    chunk_type=chunk.chunk_type,
                )
            )

        if results:
            return results

        return self._keyword_search(query, k, language, preferred_types, forbidden_types)

    def search(
        self,
        query: str,
        k: int = TOP_K,
        language: str | None = None,
        preferred_types: set[str] | None = None,
        forbidden_types: set[str] | None = None,
    ) -> list[RetrievedChunk]:
        return self._fused_search(query, k, language, preferred_types, forbidden_types)

    @staticmethod
    def format_context(chunks: list[RetrievedChunk]) -> str:
        lines = []
        for idx, c in enumerate(chunks, start=1):
            lines.append(f"[{idx}] type={c.chunk_type} | source={c.source} | snippet={c.snippet}")
        return "\n".join(lines)
