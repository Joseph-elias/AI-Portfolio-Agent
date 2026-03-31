from ..models.schemas import SourceItem
from .retrieval import RetrievedChunk


def build_sources(chunks: list[RetrievedChunk]) -> list[SourceItem]:
    return [SourceItem(source=c.source, snippet=c.snippet) for c in chunks]
