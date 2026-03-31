import json
from pathlib import Path

from app.core.config import RAW_DATA_DIR, STRUCTURED_DATA_DIR


class ProfileLoader:
    def __init__(self) -> None:
        self.skills = self._read_json(STRUCTURED_DATA_DIR / "skills.json", default={})
        self.projects = self._read_json(STRUCTURED_DATA_DIR / "projects.json", default=[])
        self.certifications = self._read_json(STRUCTURED_DATA_DIR / "certifications.json", default=[])
        self.preferences = self._read_json(STRUCTURED_DATA_DIR / "preferences.json", default={})

    @staticmethod
    def _read_json(path: Path, default):
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8-sig") as f:
            return json.load(f)

    @staticmethod
    def read_text(path: Path) -> str:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8-sig")

    @staticmethod
    def read_pdf(path: Path) -> str:
        if not path.exists():
            return ""
        try:
            from pypdf import PdfReader
        except Exception:
            return ""
        try:
            reader = PdfReader(str(path))
            parts = []
            for page in reader.pages:
                text = page.extract_text() or ""
                if text.strip():
                    parts.append(text)
            return "\n\n".join(parts)
        except Exception:
            return ""

    def all_raw_docs(self) -> list[tuple[str, str]]:
        docs = []
        for path in RAW_DATA_DIR.rglob("*"):
            if path.suffix.lower() == ".md":
                docs.append((str(path.relative_to(RAW_DATA_DIR)).replace("\\", "/"), self.read_text(path)))
            if path.suffix.lower() == ".pdf":
                docs.append((str(path.relative_to(RAW_DATA_DIR)).replace("\\", "/"), self.read_pdf(path)))
        return docs


