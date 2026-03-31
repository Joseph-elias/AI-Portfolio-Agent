from .retrieval import RetrievalService


def build_index() -> int:
    service = RetrievalService()
    return len(service.search("portfolio"))
