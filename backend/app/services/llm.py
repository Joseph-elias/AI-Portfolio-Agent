from __future__ import annotations

import re

from app.core.config import OPENAI_API_KEY, OPENAI_CHAT_MODEL, USE_OPENAI
from app.core.prompts import ABOUT_ME_SYSTEM_PROMPT, JOB_FIT_SYSTEM_PROMPT
from app.services.profile_loader import ProfileLoader

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


def _normalize_output(text: str) -> str:
    cleaned = text.strip()
    replacements = [
        "Evidence-grounded summary:",
        "Resume base sur les preuves disponibles:",
        "Summary:",
        "Result:",
        "Resultat:",
    ]
    for token in replacements:
        if cleaned.lower().startswith(token.lower()):
            cleaned = cleaned[len(token):].strip()

    cleaned = cleaned.replace("\n###", "\n").replace("\n##", "\n").replace("\n#", "\n")
    return cleaned.strip()


def _clean_snippet(snippet: str) -> str:
    text = snippet.replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\bQ:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bA:\s*", "", text, flags=re.IGNORECASE)
    if len(text) > 150:
        text = text[:147].rstrip() + "..."
    return text


class ResponseComposer:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=OPENAI_API_KEY) if (USE_OPENAI and OpenAI is not None) else None
        self.loader = ProfileLoader()

    @property
    def enabled(self) -> bool:
        return self.client is not None

    def _fallback_about(
        self,
        language: str,
        message: str,
        snippets: list[str],
        source_names: list[str] | None = None,
    ) -> str:
        msg = message.lower()
        source_names = source_names or []
        projects = [p.get("name", "") for p in self.loader.projects]
        frameworks = self.loader.skills.get("frameworks", [])
        tools = self.loader.skills.get("tools", [])

        if any(x in msg for x in ["source", "sources", "evidence", "proof", "reference", "references"]):
            listed = source_names[:5]
            points = [_clean_snippet(s) for s in snippets[:2] if s]
            if language == "fr":
                lines = ["Preuves d experience:"]
                lines.extend([f"- {p}" for p in points])
                if listed:
                    lines.append("Sources utilisees:")
                    lines.extend([f"- {s}" for s in listed])
                return "\n".join(lines)

            lines = ["Experience evidence:"]
            lines.extend([f"- {p}" for p in points])
            if listed:
                lines.append("Sources used:")
                lines.extend([f"- {s}" for s in listed])
            return "\n".join(lines)

        if any(x in msg for x in ["backend", "api", "back-end"]):
            if language == "fr":
                return (
                    "Projets backend les plus representatifs:\n"
                    "- SISSI\n"
                    "- LegalChatbot\n"
                    "- Local-RAG\n"
                    "Ils montrent FastAPI, architecture API, retrieval et integration production."
                )
            return (
                "Best backend-focused projects:\n"
                "- SISSI\n"
                "- LegalChatbot\n"
                "- Local-RAG\n"
                "They demonstrate FastAPI, API architecture, retrieval pipelines, and production integration."
            )

        if any(x in msg for x in ["strength", "strong", "best skill", "top ai engineering", "points forts", "competences"]):
            if language == "fr":
                return (
                    "Top points forts:\n"
                    "- Systemes RAG/LLM\n"
                    "- Architecture backend API\n"
                    "- Mise en production\n"
                    f"Stack principal: {', '.join(frameworks[:3])}, {', '.join(tools[:2])}."
                )
            return (
                "Top strengths:\n"
                "- RAG/LLM systems\n"
                "- Backend API architecture\n"
                "- Production-focused delivery\n"
                f"Core stack: {', '.join(frameworks[:3])}, {', '.join(tools[:2])}."
            )

        if any(x in msg for x in ["why should", "why hire", "hire", "pourquoi", "recruter"]):
            if language == "fr":
                return (
                    "Pourquoi le recruter:\n"
                    "- Il transforme des donnees complexes en solutions IA deployables\n"
                    "- Il combine execution rapide, approche produit et fiabilite backend"
                )
            return (
                "Why hire him:\n"
                "- He turns complex data into practical, deployable AI solutions\n"
                "- He combines fast execution, product thinking, and reliable backend delivery"
            )

        if "rag" in msg:
            rag_projects = [p for p in projects if any(k in p.lower() for k in ["rag", "sissi", "legalchatbot", "portfolio"])]
            if language == "fr":
                return (
                    "Oui, il a une experience RAG solide.\n"
                    f"Projets pertinents: {', '.join(rag_projects[:4])}.\n"
                    "Il a travaille sur retrieval, embeddings, citations et pipelines LLM orientes production."
                )
            return (
                "Yes, he has solid RAG experience.\n"
                f"Relevant projects: {', '.join(rag_projects[:4])}.\n"
                "He worked on retrieval, embeddings, source citations, and production-oriented LLM pipelines."
            )

        if any(x in msg for x in ["data scientist", "datascientist", "data science"]):
            if language == "fr":
                return (
                    "Oui, ce role est coherent avec son profil.\n"
                    "Il a travaille en data science medicale a l Institut Curie sur des modeles multimodaux (180+ patients) et des contributions radiomiques integrees dans LIFEx."
                )
            return (
                "Yes, this role is aligned with his profile.\n"
                "He worked in medical data science at Institut Curie on multimodal models (180+ patients) and radiomics contributions integrated into LIFEx."
            )

        if any(x in msg for x in ["project", "projet"]):
            default_order = ["SISSI", "Polished AI", "Radiomics / LIFEx Contribution", "LegalChatbot"]
            if language == "fr":
                return (
                    "Projets a prioriser:\n"
                    + "\n".join([f"- {p}" for p in default_order])
                    + "\nIl ajuste ensuite la selection selon les exigences du poste."
                )
            return (
                "Projects to prioritize:\n"
                + "\n".join([f"- {p}" for p in default_order])
                + "\nThen he adapts project focus to the specific job description."
            )

        top = _clean_snippet(snippets[0]) if snippets else ""
        if language == "fr":
            if top:
                return f"Joseph a une experience pertinente en IA et backend. Point cle: {top}"
            return "Joseph a une experience solide en IA appliquee, backend et systemes RAG."

        if top:
            return f"Joseph has relevant AI and backend experience. Key point: {top}"
        return "Joseph has strong applied AI, backend, and RAG experience."

    def compose_about_answer(
        self,
        language: str,
        message: str,
        snippets: list[str],
        sources_context: str,
        history: list[dict[str, str]] | None = None,
        source_names: list[str] | None = None,
    ) -> str:
        if not self.enabled:
            return self._fallback_about(language, message, snippets, source_names)

        history = history or []
        dialogue = "\n".join([f"{h['role']}: {h['content']}" for h in history[-6:]])

        user_prompt = (
            f"Language: {language}\n"
            f"Conversation history:\n{dialogue if dialogue else '(none)'}\n\n"
            f"User message: {message}\n\n"
            "Retrieved evidence chunks:\n"
            f"{sources_context}\n\n"
            "Respond conversationally as Agent Joseph in third person. "
            "Be organized: use short structure with headings and bullet points when the user asks for sources/evidence or requests lists. "
            "Do not use markdown # headings. "
            "Stay factual and grounded in evidence only."
        )

        try:
            response = self.client.responses.create(
                model=OPENAI_CHAT_MODEL,
                input=[
                    {"role": "system", "content": ABOUT_ME_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.35,
                max_output_tokens=420,
            )
            text = _normalize_output(getattr(response, "output_text", ""))
            return text or self._fallback_about(language, message, snippets, source_names)
        except Exception:
            return self._fallback_about(language, message, snippets, source_names)

    def compose_job_fit_summary(
        self,
        language: str,
        fit_label: str,
        score: int,
        matched: list[str],
        missing: list[str],
        relevant_projects: list[str],
        sources_context: str,
    ) -> str:
        if not self.enabled:
            if language == "fr":
                return (
                    f"Joseph montre un fit {fit_label} ({score}/100). "
                    f"Competences alignees: {', '.join(matched) if matched else 'aucune explicite'}. "
                    f"Points a renforcer: {', '.join(missing) if missing else 'pas de manque critique detecte'}."
                )
            return (
                f"Joseph looks like a {fit_label} ({score}/100). "
                f"Matched skills: {', '.join(matched) if matched else 'no explicit match found'}. "
                f"Gaps to address: {', '.join(missing) if missing else 'no critical gap detected'}."
            )

        user_prompt = (
            f"Language: {language}\n"
            f"Fit label: {fit_label}\n"
            f"Fit score: {score}\n"
            f"Matched skills: {matched}\n"
            f"Missing skills: {missing}\n"
            f"Relevant projects: {relevant_projects}\n\n"
            "Evidence:\n"
            f"{sources_context}\n\n"
            "Write a concise, natural recruiter-facing summary with clean structure and short bullet points."
        )

        try:
            response = self.client.responses.create(
                model=OPENAI_CHAT_MODEL,
                input=[
                    {"role": "system", "content": JOB_FIT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_output_tokens=300,
            )
            text = _normalize_output(getattr(response, "output_text", ""))
            if text:
                return text
        except Exception:
            pass

        if language == "fr":
            return (
                f"Joseph montre un fit {fit_label} ({score}/100). "
                f"Competences alignees: {', '.join(matched) if matched else 'aucune explicite'}. "
                f"Points a renforcer: {', '.join(missing) if missing else 'pas de manque critique detecte'}."
            )
        return (
            f"Joseph looks like a {fit_label} ({score}/100). "
            f"Matched skills: {', '.join(matched) if matched else 'no explicit match found'}. "
            f"Gaps to address: {', '.join(missing) if missing else 'no critical gap detected'}."
        )