from __future__ import annotations

import re

from ..core.config import FORCE_LLM_CHAT, OPENAI_API_KEY, OPENAI_CHAT_MODEL, USE_OPENAI
from ..core.prompts import ABOUT_ME_SYSTEM_PROMPT, JOB_FIT_SYSTEM_PROMPT
from .profile_loader import ProfileLoader

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


def _looks_incomplete(text: str) -> bool:
    if not text:
        return True
    stripped = text.rstrip()
    if stripped.endswith("..."):
        return True
    return stripped[-1] not in ".!?)\"'"


def _clean_snippet(snippet: str, max_len: int = 150, add_ellipsis: bool = True) -> str:
    text = snippet.replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\bQ:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bA:\s*", "", text, flags=re.IGNORECASE)
    if "?" in text:
        left, right = text.split("?", 1)
        right = right.strip()
        if right.lower().startswith(("yes", "no", "oui", "non")):
            text = right
    if len(text) > max_len:
        text = text[:max_len].rstrip()
        if add_ellipsis:
            text = text.rstrip(".") + "..."
    return text


def _extract_experience_highlights(snippets: list[str], language: str) -> str:
    selected: list[str] = []
    seen: set[str] = set()
    keys = [
        "institut curie",
        "u1288",
        "inserm",
        "lifex",
        "manuscript",
        "publication",
        "alternance",
        "apprenticeship",
        "stage m1",
        "internship",
        "03/2024",
        "08/2024",
        "09/2024",
        "09/2025",
        "01/2026",
        "present",
        "sissi",
        "co-founder",
        "180+",
        "40%",
    ]

    for snippet in snippets:
        cleaned = _clean_snippet(snippet, max_len=320, add_ellipsis=False)
        low = cleaned.lower()
        if any(k in low for k in keys):
            key = cleaned[:120].lower()
            if key in seen:
                continue
            seen.add(key)
            selected.append(cleaned)
        if len(selected) >= 4:
            break

    if not selected:
        return ""

    if language == "fr":
        return "Points d experience a prioriser:\n" + "\n".join(f"- {x}" for x in selected)
    return "Experience points to prioritize:\n" + "\n".join(f"- {x}" for x in selected)



def _has_certification_for_tech(certifications: list[dict], tech_terms: list[str]) -> str | None:
    if not certifications or not tech_terms:
        return None

    normalized = [t.lower() for t in tech_terms]
    alias_map = {
        "k8s": "kubernetes",
        "langchain": "langchain",
        "llamaindex": "llamaindex",
        "airflow": "airflow",
        "terraform": "terraform",
        "kafka": "kafka",
        "redis": "redis",
        "pyspark": "spark",
        "spark": "spark",
    }

    for cert in certifications:
        name = str(cert.get("name", "")).lower()
        issuer = str(cert.get("issuer", "")).lower()
        combined = f"{name} {issuer}".strip()
        for term in normalized:
            key = alias_map.get(term, term)
            if key and key in combined:
                return key
    return None


def _certification_reply_if_applicable(
    language: str,
    message: str,
    certifications: list[dict],
) -> str | None:
    msg = message.lower()
    tech_terms = [
        "kubernetes", "k8s", "langchain", "llamaindex", "airflow", "terraform", "kafka", "redis", "pyspark", "spark"
    ]
    asked_experience = any(x in msg for x in ["experience", "used", "work with", "know", "have you", "did you use"])
    asked_tech = [t for t in tech_terms if t in msg]
    if not (asked_experience and asked_tech):
        return None

    certified_tech = _has_certification_for_tech(certifications, asked_tech)
    if not certified_tech:
        return None

    if language == "fr":
        return (
            f"Oui, j ai une certification en {certified_tech}. "
            "Je n ai pas encore forcement d experience production longue sur chaque cas, "
            "mais je peux etre operationnel rapidement et je suis un apprenant rapide."
        )
    return (
        f"Yes, I have certification training in {certified_tech}. "
        "I may not yet have long production exposure in every scenario, "
        "but I can ramp up quickly and I am a fast learner."
    )


def _asks_skill_experience(msg: str) -> bool:
    patterns = [
        "experience", "used", "work with", "worked with", "know", "have you", "did you use",
        "familiar with", "background in", "exposure to", "experience in",
        "experience avec", "experience en", "tu connais", "vous connaissez", "maitrises",
    ]
    return any(p in msg for p in patterns)


def _skill_mentioned(text: str, skill: str) -> bool:
    s = skill.strip().lower()
    if not s:
        return False

    # Strict boundary for short alpha skills (e.g., c, r, sql).
    if len(s) <= 3 and s.isalpha():
        return bool(re.search(rf"\b{re.escape(s)}\b", text))

    variants = {s}
    if s.endswith("s") and len(s) > 4:
        variants.add(s[:-1])
    elif len(s) > 4:
        variants.add(s + "s")

    for v in variants:
        if re.fullmatch(r"[a-z0-9._+\-/ ]+", v):
            if re.search(rf"(?<![a-z0-9]){re.escape(v)}(?![a-z0-9])", text):
                return True
        elif v in text:
            return True

    return False


def _profile_skill_terms(skills: dict) -> list[str]:
    values: list[str] = []
    for v in skills.values():
        if isinstance(v, list):
            values.extend([x for x in v if isinstance(x, str)])

    # Add high-value aliases often used in recruiter questions.
    values.extend([
        "knowledge graph", "knowledge graphs", "neo4j", "mcp", "model context protocol"
    ])

    seen: set[str] = set()
    out: list[str] = []
    for s in values:
        k = s.strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(k)
    return out


def _profile_skill_reply_if_applicable(
    language: str,
    message: str,
    skills: dict,
    certifications: list[dict],
) -> str | None:
    msg = message.lower()
    if not _asks_skill_experience(msg):
        return None

    terms = _profile_skill_terms(skills)
    matched = [term for term in terms if _skill_mentioned(msg, term)]
    if not matched:
        return None

    matched.sort(key=len, reverse=True)
    primary = matched[0]
    certified_term = _has_certification_for_tech(certifications, matched[:12])

    if language == "fr":
        if "knowledge graph" in primary:
            return (
                "Oui, j ai de l experience avec les knowledge graphs via mon parcours master et des projets, "
                "notamment un portfolio avec Neo4j. "
                "Je peux les appliquer dans des architectures IA orientees produit, et je suis un apprenant rapide."
            )
        if certified_term:
            return (
                f"Oui, j ai de l experience sur {primary} et une certification associee ({certified_term}). "
                "Je l ai pratique dans mon parcours/projets et je peux monter rapidement en production."
            )
        return (
            f"Oui, j ai une experience sur {primary} via mon parcours master et des projets pratiques. "
            "Je peux le mobiliser dans des contextes IA/produit, et je suis un apprenant rapide."
        )

    if "knowledge graph" in primary:
        return (
            "Yes, I have experience with knowledge graphs through my master's track and project work, "
            "including a Neo4j portfolio. "
            "I can apply them in product-oriented AI architectures, and I am a fast learner."
        )
    if certified_term:
        return (
            f"Yes, I have experience with {primary} and related certification training ({certified_term}). "
            "I have used it through my academic/project track and can ramp quickly to production depth."
        )
    return (
        f"Yes, I have experience with {primary} through my master's track and hands-on projects. "
        "I can apply it in AI engineering contexts, and I am a fast learner."
    )

def _education_reply_if_applicable(language: str, message: str) -> str | None:
    msg = message.lower()
    edu_signals = [
        "education", "educational", "study", "studies", "academic", "degree", "bachelor", "master",
        "universit", "ecole", "school", "diploma", "formation", "etudes", "parcours",
    ]
    if not any(s in msg for s in edu_signals):
        return None

    bachelor_focus = any(s in msg for s in ["bachelor", "licence", "undergraduate"])

    if language == "fr":
        if bachelor_focus:
            return (
                "Oui. J ai une Licence en Genie Biomedical a la Lebanese International University (LIU), "
                "avec mention Tres Bien."
            )
        return (
            "Mon parcours comprend un Master en Ingenierie de la Sante (parcours IA en sante), "
            "suivi entre l Ecole Centrale de Lille et l Universite de Lille, avec mention Tres Bien. "
            "Avant cela, j ai obtenu une Licence en Genie Biomedical a la Lebanese International University (LIU), "
            "egalement avec mention Tres Bien."
        )

    if bachelor_focus:
        return (
            "Yes. I hold a Bachelor's degree in Biomedical Engineering from Lebanese International University (LIU), "
            "with high honors (Tres Bien)."
        )
    return (
        "My education includes a Master's in Engineering of Health (AI in Health track), completed between "
        "Ecole Centrale de Lille and Universite de Lille, with high honors (Tres Bien). "
        "Before that, I earned a Bachelor's degree in Biomedical Engineering from Lebanese International University (LIU), "
        "also with high honors (Tres Bien)."
    )


def _contract_reply_if_applicable(language: str, message: str) -> str | None:
    msg = message.lower()

    explicit_contract_signals = [
        "contract", "contracts", "cdi", "cdd", "full-time", "permanent", "emploi", "contrat", "type de contrat",
        "what type of contract", "contract type", "looking for internship", "targeting internship",
    ]
    if not any(s in msg for s in explicit_contract_signals):
        return None

    if language == "fr":
        return (
            "Je recherche actuellement des postes en CDI ou CDD. "
            "Je ne cible pas de contrat de stage pour le moment."
        )
    return (
        "I am currently looking for CDI or CDD opportunities. "
        "I am not targeting internship contracts at the moment."
    )


def _internship_experience_reply_if_applicable(language: str, message: str) -> str | None:
    msg = message.lower()
    internship_terms = ["internship", "alternance", "apprenticeship", "stage"]
    asks_experience = any(x in msg for x in ["experience", "have you", "did you", "work", "worked", "background"])
    if not (asks_experience and any(t in msg for t in internship_terms)):
        return None

    if language == "fr":
        return (
            "Oui. J ai les deux: un stage M1 en IA a l Institut Curie (03/2024-08/2024) "
            "et une alternance M2 comme Data Scientist en imagerie medicale a l Institut Curie (09/2024-09/2025)."
        )
    return (
        "Yes. I have both: an M1 AI internship at Institut Curie (March 2024-August 2024) "
        "and an M2 alternance/apprenticeship as a Data Scientist in medical imaging at Institut Curie (September 2024-September 2025)."
    )


def _self_intro_reply_if_applicable(language: str, message: str) -> str | None:
    msg = message.lower()
    intro_signals = [
        "present yourself", "introduce yourself", "tell me about yourself", "self introduction",
        "who are you", "presentation", "presente toi", "presentez vous", "parle moi de toi",
    ]
    if not any(s in msg for s in intro_signals):
        return None

    if language == "fr":
        return (
            "Je suis Ingenieur IA avec une experience de bout en bout en IA appliquee, data science et integration backend en production. "
            "Je suis actuellement AI Engineer et cofondateur chez SISSI, ou je construis des pipelines LLM, de la recherche semantique et des integrations produit. "
            "Avant cela, j ai travaille a l Institut Curie en IA medicale (alternance M2 et stage M1), avec modelisation de survie, radiomique et pipelines reproductibles."
        )
    return (
        "I am an AI Engineer with end-to-end experience in applied AI, data science, and production backend integration. "
        "I am currently AI Engineer and Co-founder at SISSI, where I build LLM pipelines, semantic retrieval systems, and product-ready backend integrations. "
        "Before that, I worked at Institut Curie in medical imaging AI (M2 alternance and M1 internship), including survival modeling, radiomics work, and reproducible pipelines."
    )


def _professional_experience_reply_if_applicable(language: str, message: str) -> str | None:
    msg = message.lower()
    signals = ["professional experience", "work experience", "experience", "worked before", "roles", "positions"]
    if not any(s in msg for s in signals):
        return None

    # Avoid overriding very specific skill or education questions.
    if any(x in msg for x in ["knowledge graph", "langchain", "kubernetes", "education", "bachelor", "master"]):
        return None

    if language == "fr":
        return (
            "Mon experience professionnelle inclut mon role actuel d AI Engineer et cofondateur chez SISSI, "
            "ou je construis des pipelines LLM, de la recherche semantique et des integrations backend. "
            "Avant cela, j ai travaille a l Institut Curie comme Data Scientist en imagerie medicale en alternance M2, "
            "et j y ai aussi realise un stage M1 en IA."
        )
    return (
        "My professional experience includes my current role as AI Engineer and Co-founder at SISSI, "
        "where I build LLM pipelines, semantic retrieval systems, and backend integrations. "
        "Before that, I worked at Institut Curie as a Data Scientist in medical imaging during my M2 alternance, "
        "and I also completed an M1 AI internship there."
    )


def _publication_reply_if_applicable(language: str, message: str) -> str | None:
    msg = message.lower()
    if not any(x in msg for x in ["publication", "paper", "manuscript", "published", "article"]):
        return None

    if language == "fr":
        return (
            "Oui. Un manuscrit scientifique est en cours a partir de mes travaux a l Institut Curie "
            "(modele de survie en cancer du poumon et nouvelles features radiomiques integrees dans LIFEx)."
        )
    return (
        "Yes. A scientific manuscript is in progress based on my Institut Curie work "
        "(lung-cancer survival modeling and newly validated radiomic features integrated into LIFEx)."
    )


def _intent_instructions(intent: str, language: str) -> str:
    fr = language == "fr"

    if intent == "experience":
        return (
            "Priority: answer with concrete work history first. Mention specific role titles, organizations, and periods when evidence exists. "
            "Do not talk about future targets, preferred roles, or aspirations unless the user explicitly asks about goals. "
            "If the evidence includes timeline signals, include them. If SISSI/current role evidence exists, start with that role first, then present Institut Curie experience. Add one short closing mention of notable GitHub projects and certifications when relevant."
            if not fr
            else "Priorite: repondre d abord avec l historique reel d experience. Mentionner les titres de poste, organisations et periodes quand les preuves existent. "
            "Ne pas parler des objectifs futurs, roles cibles ou aspirations sauf si la question porte explicitement dessus. "
            "Si des indications temporelles existent dans les preuves, les inclure. Si les preuves montrent SISSI/role actuel, commencer par ce role puis enchaIner avec l experience Institut Curie. Ajouter une courte mention des projets GitHub et certifications si pertinent."
        )

    if intent == "project":
        return (
            "Priority: mention concrete projects and delivered outcomes before general profile statements."
            if not fr
            else "Priorite: mentionner les projets concrets et resultats avant les formulations generales."
        )

    if intent == "skills":
        return (
            "Priority: map skills to evidence-backed examples from projects or work experience."
            if not fr
            else "Priorite: relier les competences a des exemples preuves dans les projets ou experiences."
        )

    return (
        "Priority: answer naturally and specifically based on the strongest retrieved evidence."
        if not fr
        else "Priorite: repondre de facon naturelle et specifique a partir des meilleures preuves recuperees."
    )


class ResponseComposer:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=OPENAI_API_KEY) if (USE_OPENAI and OpenAI is not None) else None
        self.loader = ProfileLoader()

    @property
    def enabled(self) -> bool:
        return self.client is not None

    @property
    def disabled_reason(self) -> str:
        if self.client is not None:
            return ""
        if not USE_OPENAI:
            return "OPENAI_API_KEY is missing"
        if OpenAI is None:
            return "openai package import failed"
        return "OpenAI client unavailable"

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
        certifications = getattr(self.loader, "certifications", [])

        education_reply = _education_reply_if_applicable(language, message)
        if education_reply:
            return education_reply

        education_reply = _education_reply_if_applicable(language, message)
        if education_reply:
            return education_reply

        publication_reply = _publication_reply_if_applicable(language, message)
        if publication_reply:
            return publication_reply

        intro_reply = _self_intro_reply_if_applicable(language, message)
        if intro_reply:
            return intro_reply

        internship_reply = _internship_experience_reply_if_applicable(language, message)
        if internship_reply:
            return internship_reply

        contract_reply = _contract_reply_if_applicable(language, message)
        if contract_reply:
            return contract_reply

        professional_reply = _professional_experience_reply_if_applicable(language, message)
        if professional_reply:
            return professional_reply

        skill_reply = _profile_skill_reply_if_applicable(language, message, self.loader.skills, certifications)
        if skill_reply:
            return skill_reply

        cert_reply = _certification_reply_if_applicable(language, message, certifications)
        if cert_reply:
            return cert_reply

        if any(x in msg for x in ["source", "sources", "evidence", "proof", "reference", "references"]):
            listed = source_names[:5]
            points = [_clean_snippet(s, max_len=160, add_ellipsis=True) for s in snippets[:2] if s]
            if language == "fr":
                lines = ["Preuves d experience :"]
                lines.extend([f"- {p}" for p in points])
                if listed:
                    lines.append("Sources utilisees :")
                    lines.extend([f"- {s}" for s in listed])
                return "\n".join(lines)

            lines = ["Experience evidence:"]
            lines.extend([f"- {p}" for p in points])
            if listed:
                lines.append("Sources used:")
                lines.extend([f"- {s}" for s in listed])
            return "\n".join(lines)

        if any(x in msg for x in ["who are you", "who are u", "qui es-tu", "qui es tu", "are you joseph"]) or re.search(r"\bare you\?\s*$", msg):
            if language == "fr":
                return (
                    "Je suis un Ingenieur IA avec une experience de bout en bout en IA appliquee, data science et integration backend en production. "
                    "Je suis actuellement AI Engineer et cofondateur chez SISSI, ou je construis des pipelines LLM, de la recherche semantique avec embeddings et pgvector, et des modules IA dans une architecture React, Django REST et Supabase. "
                    "Avant cela, j ai travaille a l Institut Curie en IA medicale pendant mon stage M1 et mon alternance M2, avec modelisation de survie, optimisation radiomique et pipelines reproductibles."
                )
            return (
                "I am an AI Engineer with end-to-end experience in applied AI, data science, and production backend integration. "
                "I am currently AI Engineer and Co-founder at SISSI, where I build LLM pipelines, semantic retrieval with embeddings and pgvector, and AI modules inside a React, Django REST, and Supabase SaaS architecture. "
                "Before that, I worked at Institut Curie in medical imaging AI through both my M1 internship and M2 alternance, including survival modeling, radiomics optimization, and reproducible research pipelines."
            )

        if any(x in msg for x in ["stand out", "special", "unique", "what makes", "different", "differentiate", "distinct"]):
            if language == "fr":
                return (
                    "Ce qui me distingue, c est le mix IA appliquee, approche produit et execution backend fiable. "
                    "Je livre des systemes RAG clairs, sourcees, et deployables, pas seulement des demos."
                )
            return (
                "What stands out is the mix of applied AI, product thinking, and reliable backend execution. "
                "I ship RAG systems that are source-grounded and deployable, not just demos."
            )

        tech_terms = [
            "kubernetes", "k8s", "langchain", "llamaindex", "airflow", "terraform", "kafka", "redis", "pyspark", "spark"
        ]
        asked_experience = any(x in msg for x in ["experience", "used", "work with", "know", "have you", "did you use"])
        asked_plan = any(x in msg for x in ["30 days", "first month", "ramp", "plan", "how would you", "learning plan"])
        asked_tech = [t for t in tech_terms if t in msg]
        if asked_tech and asked_experience:
            tech_label = ", ".join(sorted(set(asked_tech)))
            if language == "fr":
                if asked_plan:
                    return (
                        f"Je n ai pas encore d experience de production documentee sur {tech_label}, mais je suis un apprenant rapide. "
                        "Mon plan sur 30 jours serait: semaine 1 fondamentaux et architecture, semaine 2 pratique ciblee avec mini implementation, "
                        "semaine 3 integration dans un workflow proche production, semaine 4 durcissement, monitoring et revue avec l equipe. "
                        "J ai deja une base solide en outils adjacents (Docker, FastAPI, pipelines RAG, systemes backend)."
                    )
                return (
                    f"Je n ai pas encore d experience de production documentee sur {tech_label}. "
                    "En revanche, j ai une base solide en outils adjacents (Docker, FastAPI, pipelines RAG, systemes backend), "
                    "et je suis un apprenant rapide qui monte vite en competence."
                )
            if asked_plan:
                return (
                    f"I do not yet have direct documented production experience with {tech_label}, but I am a fast learner. "
                    "My 30-day ramp plan would be: week 1 fundamentals and architecture patterns, week 2 hands-on lab + mini implementation, "
                    "week 3 integration into one production-style workflow, and week 4 hardening, monitoring, and review with the team. "
                    "I already bring adjacent strengths in Docker, FastAPI, RAG pipelines, and backend systems. "
                )
            return (
                f"I do not yet have direct documented production experience with {tech_label}. "
                "That said, I have strong adjacent experience (Docker, FastAPI, RAG pipelines, backend systems), "
                "and I am a fast learner who ramps up quickly on new stacks."
            )

        if any(x in msg for x in ["backend", "api", "back-end"]):
            if language == "fr":
                return (
                    "Mes projets backend les plus representatifs sont SISSI, LegalChatbot et Local-RAG. "
                    "Ils montrent FastAPI, architecture API, retrieval et integration production."
                )
            return (
                "My most representative backend projects are SISSI, LegalChatbot, and Local-RAG. "
                "They show FastAPI, API architecture, retrieval pipelines, and production integration."
            )

        if any(x in msg for x in ["strength", "strong", "best skill", "top ai engineering", "points forts", "competences"]):
            if language == "fr":
                return (
                    "Mes points forts sont les systemes RAG/LLM, l architecture backend API et la mise en production. "
                    f"Stack principal: {', '.join(frameworks[:3])}, {', '.join(tools[:2])}."
                )
            return (
                "My core strengths are RAG/LLM systems, backend API architecture, and production delivery. "
                f"Core stack: {', '.join(frameworks[:3])}, {', '.join(tools[:2])}."
            )

        if any(x in msg for x in ["why should", "why hire", "hire", "pourquoi", "recruter"]):
            if language == "fr":
                return (
                    "Je transforme des donnees complexes en solutions IA deployables et je combine execution rapide, "
                    "approche produit et fiabilite backend."
                )
            return (
                "I turn complex data into practical, deployable AI solutions and combine fast execution, "
                "product thinking, and reliable backend delivery."
            )

        if "rag" in msg:
            rag_projects = [p for p in projects if any(k in p.lower() for k in ["rag", "sissi", "legalchatbot", "portfolio"])]
            if language == "fr":
                return (
                    "Oui, j ai une experience RAG solide. "
                    f"Projets pertinents: {', '.join(rag_projects[:4])}. "
                    "J ai travaille sur retrieval, embeddings, citations et pipelines LLM orientes production."
                )
            return (
                "Yes, I have solid RAG experience. "
                f"Relevant projects: {', '.join(rag_projects[:4])}. "
                "I worked on retrieval, embeddings, source citations, and production-oriented LLM pipelines."
            )

        top = _clean_snippet(snippets[0], max_len=420, add_ellipsis=False) if snippets else ""
        if top.endswith("?"):
            top = ""
        if language == "fr":
            if top:
                return f"J ai une experience pertinente en IA et backend. {top}"
            return "J ai une experience solide en IA appliquee, backend et systemes RAG."

        if top:
            return f"I have relevant AI and backend experience. {top}"
        return "I have strong applied AI, backend, and RAG experience."

    def compose_about_answer(
        self,
        language: str,
        message: str,
        snippets: list[str],
        sources_context: str,
        history: list[dict[str, str]] | None = None,
        source_names: list[str] | None = None,
        intent: str = "general",
    ) -> str:
        certifications = getattr(self.loader, "certifications", [])

        if not self.enabled or not FORCE_LLM_CHAT:
            education_reply = _education_reply_if_applicable(language, message)
            if education_reply:
                return education_reply

            education_reply = _education_reply_if_applicable(language, message)
            if education_reply:
                return education_reply

            publication_reply = _publication_reply_if_applicable(language, message)
            if publication_reply:
                return publication_reply

            intro_reply = _self_intro_reply_if_applicable(language, message)
            if intro_reply:
                return intro_reply

            internship_reply = _internship_experience_reply_if_applicable(language, message)
            if internship_reply:
                return internship_reply

            contract_reply = _contract_reply_if_applicable(language, message)
            if contract_reply:
                return contract_reply

            professional_reply = _professional_experience_reply_if_applicable(language, message)
            if professional_reply:
                return professional_reply

            skill_reply = _profile_skill_reply_if_applicable(language, message, self.loader.skills, certifications)
            if skill_reply:
                return skill_reply

            cert_reply = _certification_reply_if_applicable(language, message, certifications)
            if cert_reply:
                return cert_reply

        if not self.enabled:
            return self._fallback_about(language, message, snippets, source_names)

        history = history or []
        dialogue = "\n".join([f"{h['role']}: {h['content']}" for h in history[-6:]])
        intent_rules = _intent_instructions(intent, language)
        experience_highlights = _extract_experience_highlights(snippets, language) if intent == "experience" else ""

        user_prompt = (
            f"Language: {language}\n"
            f"Intent: {intent}\n"
            f"Conversation history:\n{dialogue if dialogue else '(none)'}\n\n"
            f"User message: {message}\n\n"
            "Retrieved evidence chunks:\n"
            f"{sources_context}\n\n"
            f"Intent rules: {intent_rules}\n"
            f"{experience_highlights}\n"
            "Respond as Agent Joseph using first person. "
            "Answer in natural short paragraphs, usually 2-6 sentences unless the user asks for a list. "
            "Do not repeat the user question. Do not ask new questions unless clarification is required. "
            "Use only evidence from the retrieved chunks and do not invent any role, company, date, skill, or project. "
            "If evidence for a requested tool/technology is missing, respond diplomatically: say there is no direct documented production experience, mention adjacent strengths, and explicitly state that I am a fast learner. "
            "If the user asks how I would close a gap, include a concise 30-day ramp plan. "
            "If evidence is insufficient, say so clearly in one sentence."
        )

        try:
            response = self.client.responses.create(
                model=OPENAI_CHAT_MODEL,
                input=[
                    {"role": "system", "content": ABOUT_ME_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.45,
            )
            text = _normalize_output(getattr(response, "output_text", ""))
            if text and _looks_incomplete(text):
                fix_prompt = (
                    f"Language: {language}\n"
                    "Complete this response naturally in 1-2 sentences without repeating it.\n"
                    "Keep the same facts and do not add new unsupported claims.\n\n"
                    f"Current response:\n{text}"
                )
                try:
                    continuation = self.client.responses.create(
                        model=OPENAI_CHAT_MODEL,
                        input=[
                            {"role": "system", "content": ABOUT_ME_SYSTEM_PROMPT},
                            {"role": "user", "content": fix_prompt},
                        ],
                        temperature=0.2,
                    )
                    tail = _normalize_output(getattr(continuation, "output_text", ""))
                    if tail:
                        text = f"{text} {tail}".strip()
                except Exception:
                    pass
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




