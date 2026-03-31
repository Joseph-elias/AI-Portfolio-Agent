from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from ..core.config import STRUCTURED_DATA_DIR
from .profile_loader import ProfileLoader


@dataclass
class IntentPlan:
    intent: str
    normalized_message: str
    required_keywords_en: list[str]


class ConsistencyEngine:
    def __init__(self) -> None:
        self.loader = ProfileLoader()
        self.truth_profile = self._read_json(STRUCTURED_DATA_DIR / "truth_profile.json", default={})
        self.intent_templates = self._read_json(STRUCTURED_DATA_DIR / "intent_templates.json", default={})

    @staticmethod
    def _read_json(path: Path, default):
        if not path.exists():
            return default
        try:
            with path.open("r", encoding="utf-8-sig") as f:
                return json.load(f)
        except Exception:
            return default

    def _synonym_map(self) -> dict[str, list[str]]:
        return self.intent_templates.get("synonyms", {}) if isinstance(self.intent_templates, dict) else {}

    def normalize_message(self, message: str) -> str:
        normalized = message.lower().replace("?", "'")
        for canonical, variants in self._synonym_map().items():
            if not isinstance(variants, list):
                continue
            for variant in variants:
                v = str(variant).lower().strip()
                if not v:
                    continue
                normalized = re.sub(rf"(?<![a-z0-9]){re.escape(v)}(?![a-z0-9])", canonical, normalized)
        return normalized

    def plan(self, message: str) -> IntentPlan:
        m = self.normalize_message(message)
        intents = self.intent_templates.get("intents", {}) if isinstance(self.intent_templates, dict) else {}

        if any(x in m for x in ["30-second intro", "30 second intro", "30s intro", "quick intro"]):
            cfg = intents.get("self_intro", {}) if isinstance(intents, dict) else {}
            required = cfg.get("required_keywords_en", []) if isinstance(cfg, dict) else []
            return IntentPlan(intent="self_intro", normalized_message=m, required_keywords_en=list(required))

        if any(x in m for x in ["bilingual", "which language", "what languages", "language can you work"]):
            cfg = intents.get("languages", {}) if isinstance(intents, dict) else {}
            required = cfg.get("required_keywords_en", []) if isinstance(cfg, dict) else []
            return IntentPlan(intent="languages", normalized_message=m, required_keywords_en=list(required))

        if "30-day" in m or "30 day" in m or "week 1" in m or "ramp plan" in m:
            cfg = intents.get("gap_plan", {}) if isinstance(intents, dict) else {}
            required = cfg.get("required_keywords_en", []) if isinstance(cfg, dict) else []
            return IntentPlan(intent="gap_plan", normalized_message=m, required_keywords_en=list(required))

        if ("skills you" in m and "do not have" in m) or ("skills you" in m and "don't have" in m) or ("if you don't know" in m):
            cfg = intents.get("gap_handling", {}) if isinstance(intents, dict) else {}
            required = cfg.get("required_keywords_en", []) if isinstance(cfg, dict) else []
            return IntentPlan(intent="gap_handling", normalized_message=m, required_keywords_en=list(required))

        if "sissi" in m and any(x in m for x in ["what did you do", "what happened", "at sissi", "tell me about sissi"]):
            return IntentPlan(intent="sissi_detail", normalized_message=m, required_keywords_en=["sissi", "llm"])

        if ("institut curie" in m or "sissi" in m) and any(x in m for x in ["what happened", "what did you do", "tell me about", "work there"]):
            cfg = intents.get("experience", {}) if isinstance(intents, dict) else {}
            required = cfg.get("required_keywords_en", []) if isinstance(cfg, dict) else []
            return IntentPlan(intent="experience", normalized_message=m, required_keywords_en=list(required))

        # Role-target questions should not be confused with past-experience questions.
        if (
            ("looking for" in m or "searching for" in m or "target" in m)
            and any(x in m for x in ["position", "positions", "role", "roles", "job", "jobs"])
        ) or ("searching for" in m and "right now" in m) or ("looking for" in m and "right now" in m):
            cfg = intents.get("target_roles", {}) if isinstance(intents, dict) else {}
            required = cfg.get("required_keywords_en", []) if isinstance(cfg, dict) else []
            return IntentPlan(intent="target_roles", normalized_message=m, required_keywords_en=list(required))

        # Contract preference should win when user asks targeting/looking-for questions.
        if (
            ("looking for" in m or "target" in m or "preference" in m)
            and any(x in m for x in ["contract", "internship", "cdi", "cdd", "full-time", "permanent"])
        ):
            cfg = intents.get("contract", {}) if isinstance(intents, dict) else {}
            required = cfg.get("required_keywords_en", []) if isinstance(cfg, dict) else []
            return IntentPlan(intent="contract", normalized_message=m, required_keywords_en=list(required))

        skill_question_markers = ["experience with", "do you know", "have you used", "any experience in", "familiar with"]
        if any(x in m for x in skill_question_markers):
            cfg = intents.get("skills", {}) if isinstance(intents, dict) else {}
            required = cfg.get("required_keywords_en", []) if isinstance(cfg, dict) else []
            return IntentPlan(intent="skills", normalized_message=m, required_keywords_en=list(required))

        # Priority order to keep answers consistent.
        priority = [
            "self_intro",
            "education",
            "publications",
            "languages",
            "internship_experience",
            "target_roles",
            "contract",
            "experience",
            "hire",
            "gap_plan",
            "gap_handling",
            "skills",
        ]

        for name in priority:
            cfg = intents.get(name, {}) if isinstance(intents, dict) else {}
            triggers = cfg.get("triggers", []) if isinstance(cfg, dict) else []
            if any(str(t).lower() in m for t in triggers):
                required = cfg.get("required_keywords_en", []) if isinstance(cfg, dict) else []
                return IntentPlan(intent=name, normalized_message=m, required_keywords_en=list(required))

        return IntentPlan(intent="general", normalized_message=m, required_keywords_en=[])

    def _all_skills(self) -> list[str]:
        skills = self.loader.skills
        out: list[str] = []
        for v in skills.values():
            if isinstance(v, list):
                out.extend([str(x).strip() for x in v if isinstance(x, str) and str(x).strip()])
        seen: set[str] = set()
        dedup: list[str] = []
        for s in out:
            k = s.lower()
            if k in seen:
                continue
            seen.add(k)
            dedup.append(s)
        return dedup

    def _find_skill_mention(self, normalized_message: str) -> str | None:
        alias_map = {
            "model context protocol": "Model Context Protocol",
            "mcp": "Model Context Protocol",
            "knowledge graph": "Knowledge Graphs",
            "knowledge graphs": "Knowledge Graphs",
            "neo4j": "Knowledge Graphs",
            "airflow": "Airflow",
            "terraform": "Terraform",
            "prefect": "Prefect",
            "pgvector": "pgvector",
        }
        for alias, canonical in alias_map.items():
            if re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", normalized_message):
                return canonical

        simplified_msg = re.sub(r"[^a-z0-9 ]+", " ", normalized_message)

        for skill in self._all_skills():
            s = skill.lower()
            s_base = re.sub(r"\s*\(.*?\)", "", s).strip()
            candidates = {s, s_base}
            if len(s_base) > 4 and s_base.endswith("s"):
                candidates.add(s_base[:-1])

            for c in candidates:
                if not c:
                    continue
                c_norm = re.sub(r"[^a-z0-9 ]+", " ", c)
                if re.search(rf"(?<![a-z0-9]){re.escape(c_norm)}(?![a-z0-9])", simplified_msg):
                    return skill

        return None

    def _is_certified_for(self, skill: str) -> bool:
        certs = getattr(self.loader, "certifications", []) or []
        s = skill.lower()
        for c in certs:
            name = str(c.get("name", "")).lower()
            issuer = str(c.get("issuer", "")).lower()
            if s in name or s in issuer:
                return True
        return False

    def deterministic_answer(self, plan: IntentPlan, language: str) -> str | None:
        t = self.truth_profile
        if not isinstance(t, dict):
            return None

        if plan.intent == "self_intro":
            if language == "fr":
                return (
                    "Je suis Ingenieur IA avec une experience de bout en bout en IA appliquee, data science et integration backend en production. "
                    "Je suis actuellement AI Engineer et cofondateur chez SISSI, et avant cela j ai travaille a l Institut Curie en IA medicale."
                )
            return (
                "I am an AI Engineer with end-to-end experience in applied AI, data science, and production backend integration. "
                "I am currently AI Engineer and Co-founder at SISSI, and before that I worked at Institut Curie in medical imaging AI."
            )

        if plan.intent == "education":
            edu = t.get("education", {})
            master = edu.get("master", {})
            bachelor = edu.get("bachelor", {})
            if language == "fr":
                return (
                    f"Mon parcours comprend un {master.get('degree', 'Master')} entre {', '.join(master.get('schools', []))}, "
                    f"mention {master.get('mention', 'Tres Bien')}. "
                    f"Avant cela, j ai obtenu une {bachelor.get('degree', 'Licence')} a {bachelor.get('school', 'LIU')}, "
                    f"egalement mention {bachelor.get('mention', 'Tres Bien')}."
                )
            return (
                f"My education includes a {master.get('degree', 'Master')} completed between {', '.join(master.get('schools', []))}, "
                f"with high honors ({master.get('mention', 'Tres Bien')}). "
                f"Before that, I earned a {bachelor.get('degree', 'Bachelor')} from {bachelor.get('school', 'LIU')}, "
                f"also with high honors ({bachelor.get('mention', 'Tres Bien')})."
            )

        if plan.intent == "contract":
            pref = t.get("contract_preference", {})
            target = "/".join(pref.get("target_contracts", ["CDI", "CDD"]))
            if language == "fr":
                return f"Je recherche actuellement des opportunites en {target}. Je ne cible pas de contrat de stage pour le moment."
            return f"I am currently looking for {target} opportunities. I am not targeting internship contracts at the moment."

        if plan.intent == "target_roles":
            roles = t.get("target_roles", ["AI Engineer", "Applied AI Engineer", "LLM Engineer"])
            pref = t.get("contract_preference", {})
            contracts = "/".join(pref.get("target_contracts", ["CDI", "CDD"]))
            joined = ", ".join(roles)
            if language == "fr":
                return (
                    f"Je cible principalement les postes de {joined}, idealement sur des contrats {contracts}. "
                    "Je suis ouvert aux opportunites IA au sens large: IA appliquee, machine learning, data science, backend IA, systemes multimodaux et mise en production."
                )
            return (
                f"I am mainly targeting {joined} positions, ideally on {contracts} contracts. "
                "I am open to AI opportunities broadly, including applied AI, machine learning, data science, AI backend engineering, multimodal systems, and production AI delivery."
            )

        if plan.intent == "languages":
            if language == "fr":
                return "Je suis bilingue en francais et en anglais, et je parle aussi arabe."
            return "I am bilingual in English and French, and I also speak Arabic."

        if plan.intent == "gap_handling":
            if language == "fr":
                return "Quand une competence me manque, je suis transparent, je m appuie sur mes competences adjacentes et je monte vite en competence. Je suis un apprenant rapide."
            return "When I do not have direct depth on a skill, I stay transparent, leverage adjacent strengths, and ramp quickly. I am a fast learner."

        if plan.intent == "gap_plan":
            if language == "fr":
                return "Mon plan sur 30-day serait: week 1 fondamentaux et architecture, week 2 pratique ciblee avec mini implementation, week 3 integration dans un workflow proche production, week 4 durcissement et monitoring."
            return "My 30-day plan would be: week 1 fundamentals and architecture, week 2 focused hands-on implementation, week 3 integration into a production-like workflow, and week 4 hardening plus monitoring."

        if plan.intent == "publications":
            pub = t.get("publications", {})
            summary = pub.get("summary", "")
            if language == "fr":
                return f"Oui. {summary}" if summary else "Oui, un manuscrit scientifique est en cours sur mes travaux a l Institut Curie."
            return f"Yes. {summary}" if summary else "Yes, a scientific manuscript is in progress from my Institut Curie work."

        if plan.intent == "internship_experience":
            if language == "fr":
                return (
                    "Oui. J ai les deux: un stage M1 en IA a l Institut Curie (03/2024-08/2024) "
                    "et une alternance M2 comme Data Scientist en imagerie medicale (09/2024-09/2025)."
                )
            return (
                "Yes. I have both: an M1 AI internship at Institut Curie (March 2024-August 2024) "
                "and an M2 alternance/apprenticeship as a Data Scientist in medical imaging (September 2024-September 2025)."
            )

        if plan.intent == "experience":
            roles = t.get("roles", [])
            if len(roles) >= 2:
                first = roles[0]
                second = roles[1]
                if language == "fr":
                    return (
                        f"Mon experience professionnelle inclut d abord {first.get('title', '')} chez {first.get('company', '')}, "
                        f"puis {second.get('title', '')} chez {second.get('company', '')}."
                    )
                return (
                    f"My professional experience includes {first.get('title', '')} at {first.get('company', '')}, "
                    f"followed by {second.get('title', '')} at {second.get('company', '')}."
                )

        if plan.intent == "sissi_detail":
            if language == "fr":
                return (
                    "Chez SISSI, je con?ois des pipelines LLM pour la structuration de notes, "
                    "je mets en place la recherche semantique (embeddings, pgvector), "
                    "et j integre ces modules IA dans une architecture React, Django REST et Supabase."
                )
            return (
                "At SISSI, I design LLM pipelines for note structuring, build semantic retrieval with embeddings and pgvector, "
                "and integrate these AI modules into a React, Django REST, and Supabase architecture."
            )

        if plan.intent == "hire":
            if language == "fr":
                return (
                    "Je transforme des donnees complexes en solutions IA deployables et je combine execution rapide, "
                    "approche produit et fiabilite backend."
                )
            return (
                "I turn complex data into practical, deployable AI solutions and combine fast execution, "
                "product thinking, and reliable backend delivery."
            )

        if plan.intent == "skills":
            skill = self._find_skill_mention(plan.normalized_message)
            asks_experience = any(x in plan.normalized_message for x in ["experience", "used", "work with", "have you", "familiar"])
            if asks_experience and skill:
                certified = self._is_certified_for(skill)
                if language == "fr":
                    if certified:
                        return f"Oui, j ai de l experience avec {skill} et une certification associee. Je suis aussi un apprenant rapide."
                    return f"Oui, j ai de l experience avec {skill} via mon parcours et des projets pratiques. Je suis un apprenant rapide."
                if skill.lower() == "knowledge graphs":
                    return "Yes, I have experience with knowledge graphs, including Neo4j-based work in my portfolio and projects. I am a fast learner."
                if certified:
                    return f"Yes, I have experience with {skill} and related certification training. I am also a fast learner."
                return f"Yes, I have experience with {skill} through my track and hands-on projects. I am a fast learner."

        return None

    def validate_answer(self, answer: str, plan: IntentPlan) -> bool:
        if not answer.strip():
            return False
        required = [k.lower() for k in plan.required_keywords_en if isinstance(k, str) and k.strip()]
        if not required:
            return True
        low = answer.lower()
        return all(k in low for k in required)

    def repair_answer(self, plan: IntentPlan, language: str, current_answer: str) -> str:
        repaired = self.deterministic_answer(plan, language)
        if repaired:
            return repaired
        return current_answer
