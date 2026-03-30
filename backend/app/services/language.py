FR_HINTS = {"bonjour", "pourquoi", "quels", "quelle", "offre", "poste", "ingenieur", "experience", "competences", "projets"}


def detect_language(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in FR_HINTS):
        return "fr"
    return "en"
