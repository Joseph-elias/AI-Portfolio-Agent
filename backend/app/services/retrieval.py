from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass

from app.core.config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL, TOP_K, USE_OPENAI, VECTOR_STORE_DIR
from app.services.profile_loader import ProfileLoader

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


@dataclass
class RetrievedChunk:
    source: str
    snippet: str
    score: float


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

    def _build_chunks(self) -> list[RetrievedChunk]:
        chunks: list[RetrievedChunk] = []
        for source, text in self.loader.all_raw_docs():
            cleaned = self._clean_text_block(text)
            for part in [x.strip() for x in cleaned.split("\n\n") if x.strip()]:
                chunks.append(RetrievedChunk(source=source, snippet=part[:520], score=0.0))

        for project in self.loader.projects:
            name = project.get("name", "Unnamed project")
            summary_en = project.get("summary_en", "")
            summary_fr = project.get("summary_fr", "")
            skills = ", ".join(project.get("skills_used", []))
            payload = f"{name}. {summary_en} {summary_fr} Skills used: {skills}".strip()
            chunks.append(RetrievedChunk(source="structured/projects.json", snippet=payload[:520], score=0.0))
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
    def _source_intent_boost(source: str, query: str) -> float:
        q = query.lower()
        boost = 0.0

        if any(x in q for x in ["experience", "work", "internship", "history", "did", "background"]):
            if "experience/" in source:
                boost += 3.5
            if "resume_" in source:
                boost += 2.8
            if "projects/" in source:
                boost += 2.2
            if "faq" in source:
                boost -= 1.5

        if any(x in q for x in ["source", "sources", "evidence", "reference"]):
            if any(k in source for k in ["resume_", "projects/", "experience/"]):
                boost += 1.5

        if any(x in q for x in ["backend", "api"]):
            if "projects/" in source or "structured/projects.json" in source:
                boost += 1.8

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

    def _keyword_search(self, query: str, k: int, language: str | None) -> list[RetrievedChunk]:
        q_terms = [t for t in query.lower().split() if len(t) > 2]
        scored = []
        for c in self._chunks:
            if not self._source_matches_language(c.source, language):
                continue
            text = c.snippet.lower()
            base = float(sum(1 for t in q_terms if t in text))
            if base > 0:
                score = base + self._source_intent_boost(c.source, query)
                scored.append(RetrievedChunk(source=c.source, snippet=c.snippet, score=score))
        scored.sort(key=lambda x: x.score, reverse=True)
        if scored:
            return scored[:k]

        fallback = [c for c in self._chunks if self._source_matches_language(c.source, language)]
        return fallback[:k] if fallback else self._chunks[:k]

    def search(self, query: str, k: int = TOP_K, language: str | None = None) -> list[RetrievedChunk]:
        query_vector = self._embedding(query)
        if query_vector is None:
            return self._keyword_search(query, k, language)

        qn = self._norm(query_vector) or 1.0
        scored: list[RetrievedChunk] = []

        for c in self._chunks:
            if not self._source_matches_language(c.source, language):
                continue
            cv = self._embedding(c.snippet)
            if cv is None:
                continue
            denom = (self._norm(cv) * qn) or 1.0
            similarity = self._dot(query_vector, cv) / denom
            similarity += self._source_intent_boost(c.source, query)
            scored.append(RetrievedChunk(source=c.source, snippet=c.snippet, score=similarity))

        scored.sort(key=lambda x: x.score, reverse=True)
        top_semantic = scored[:k]
        if top_semantic:
            return top_semantic

        return self._keyword_search(query, k, language)

    @staticmethod
    def format_context(chunks: list[RetrievedChunk]) -> str:
        lines = []
        for idx, c in enumerate(chunks, start=1):
            lines.append(f"[{idx}] source={c.source} | snippet={c.snippet}")
        return "\n".join(lines)