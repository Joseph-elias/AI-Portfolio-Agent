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


@dataclass
class JobMatchResult:
    required_skills: list[str]
    matched_skills: list[str]
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
        return {v.lower() for v in all_values}

    def _known_skill_set(self) -> set[str]:
        # Keep static aliases, but prioritize dynamically loaded profile skills.
        return self._candidate_skill_set().union(KNOWN_SKILLS)

    @staticmethod
    def _skill_mentioned(lowered_jd: str, skill: str) -> bool:
        # Use strict boundaries for short/common tokens to avoid false positives.
        if len(skill) <= 2 and skill.isalpha():
            return bool(re.search(rf"\b{re.escape(skill)}\b", lowered_jd))

        # For common word-like skills, prefer boundary matching.
        if re.fullmatch(r"[a-z0-9._+-]+", skill):
            return bool(re.search(rf"(?<![a-z0-9]){re.escape(skill)}(?![a-z0-9])", lowered_jd))

        return skill in lowered_jd

    def extract_required_skills(self, jd: str) -> list[str]:
        lowered = jd.lower()
        found = [s for s in self._known_skill_set() if self._skill_mentioned(lowered, s)]
        return sorted(set(found))

    def relevant_projects(self, matched_skills: list[str]) -> list[str]:
        out = []
        for p in self.loader.projects:
            used = {s.lower() for s in p.get("skills_used", [])}
            if used.intersection(set(matched_skills)):
                out.append(p.get("name", "Unnamed project"))
        return out[:3]

    def match(self, jd: str) -> JobMatchResult:
        required = self.extract_required_skills(jd)
        candidate = self._candidate_skill_set()
        matched = [s for s in required if s in candidate]
        missing = [s for s in required if s not in candidate]
        projects = self.relevant_projects(matched)
        return JobMatchResult(
            required_skills=required,
            matched_skills=matched,
            missing_skills=missing,
            relevant_projects=projects,
        )
