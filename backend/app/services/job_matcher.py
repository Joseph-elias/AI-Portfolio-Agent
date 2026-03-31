from dataclasses import dataclass
import re

from .profile_loader import ProfileLoader


KNOWN_SKILLS = {
    "python",
    "typescript",
    "javascript",
    "sql",
    "rag",
    "llm",
    "fastapi",
    "next.js",
    "docker",
    "aws",
    "pytorch",
    "langchain",
    "faiss",
    "chroma",
    "kubernetes",
}

# Canonical skills with practical aliases used in job descriptions.
SKILL_ALIASES = {
    "llm": {"llm", "llms", "large language model", "large language models", "genai", "generative ai"},
    "rag": {"rag", "retrieval augmented generation", "retrieval-augmented generation"},
    "aws": {"aws", "amazon web services", "aws cloud"},
    "kubernetes": {"kubernetes", "k8s"},
    "next.js": {"next.js", "nextjs", "next js"},
    "typescript": {"typescript", "ts"},
    "javascript": {"javascript", "js"},
    "sql": {"sql", "postgres", "postgresql", "mysql", "sqlite", "sql server"},
    "fastapi": {"fastapi", "fast api"},
    "langchain": {"langchain", "lang chain"},
}

# Adjacent skills can get partial credit in scoring.
ADJACENT_SKILLS = {
    "aws": {"docker", "kubernetes", "terraform"},
    "kubernetes": {"docker", "aws"},
    "rag": {"llm", "langchain", "vector databases", "faiss", "chroma", "pgvector"},
    "llm": {"rag", "langchain", "prompt engineering"},
    "fastapi": {"rest apis", "microservices", "python"},
    "sql": {"postgresql", "mysql", "sqlite", "mongodb"},
}


@dataclass
class JobMatchResult:
    required_skills: list[str]
    matched_skills: list[str]
    partial_matched_skills: list[str]
    missing_skills: list[str]
    relevant_projects: list[str]


class JobMatcher:
    def __init__(self) -> None:
        self.loader = ProfileLoader()

    def _candidate_skill_set(self) -> set[str]:
        skills = self.loader.skills
        all_values = []
        for value in skills.values():
            if isinstance(value, list):
                all_values.extend(value)
        return {str(v).strip().lower() for v in all_values if str(v).strip()}

    def _known_skill_set(self) -> set[str]:
        return self._candidate_skill_set().union(KNOWN_SKILLS).union(SKILL_ALIASES.keys())

    @staticmethod
    def _skill_mentioned(lowered_jd: str, skill: str) -> bool:
        if len(skill) <= 2 and skill.isalpha():
            return bool(re.search(rf"\b{re.escape(skill)}\b", lowered_jd))

        if re.fullmatch(r"[a-z0-9._+\- ]+", skill):
            return bool(re.search(rf"(?<![a-z0-9]){re.escape(skill)}(?![a-z0-9])", lowered_jd))

        return skill in lowered_jd

    def _extract_with_aliases(self, lowered: str) -> set[str]:
        found: set[str] = set()
        for canonical, aliases in SKILL_ALIASES.items():
            if any(self._skill_mentioned(lowered, alias) for alias in aliases):
                found.add(canonical)
        return found

    def extract_required_skills(self, jd: str) -> list[str]:
        lowered = jd.lower()
        found = {s for s in self._known_skill_set() if self._skill_mentioned(lowered, s)}
        found.update(self._extract_with_aliases(lowered))
        return sorted(found)

    def relevant_projects(self, matched_skills: list[str]) -> list[str]:
        out = []
        skill_set = set(matched_skills)
        for p in self.loader.projects:
            used = {s.lower() for s in p.get("skills_used", [])}
            if used.intersection(skill_set):
                out.append(p.get("name", "Unnamed project"))
        return out[:3]

    def _is_partially_covered(self, required_skill: str, candidate_skills: set[str]) -> bool:
        neighbors = ADJACENT_SKILLS.get(required_skill, set())
        if not neighbors:
            return False
        return any(n in candidate_skills for n in neighbors)

    def match(self, jd: str) -> JobMatchResult:
        required = self.extract_required_skills(jd)
        candidate = self._candidate_skill_set()

        matched = [s for s in required if s in candidate]
        partial = [s for s in required if s not in candidate and self._is_partially_covered(s, candidate)]
        missing = [s for s in required if s not in candidate and s not in partial]

        projects = self.relevant_projects(matched + partial)
        return JobMatchResult(
            required_skills=required,
            matched_skills=matched,
            partial_matched_skills=partial,
            missing_skills=missing,
            relevant_projects=projects,
        )
