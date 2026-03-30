from app.services.retrieval import RetrievalService



def test_retrieval_returns_chunks():
    service = RetrievalService()
    out = service.search("RAG projects")
    assert len(out) > 0
