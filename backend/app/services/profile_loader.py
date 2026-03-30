import json
from pathlib import Path

from app.core.config import RAW_DATA_DIR, STRUCTURED_DATA_DIR


class ProfileLoader:
    def __init__(self) -> None:
        self.skills = self._read_json(STRUCTURED_DATA_DIR / "skills.json", default={})
        self.projects = self._read_json(STRUCTURED_DATA_DIR / "projects.json", default=[])
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

    def all_raw_docs(self) -> list[tuple[str, str]]:
        docs = []
        for path in RAW_DATA_DIR.rglob("*.md"):
            docs.append((str(path.relative_to(RAW_DATA_DIR)).replace("\\", "/"), self.read_text(path)))
        return docs
