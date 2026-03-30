from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_job_fit_endpoint():
    res = client.post(
        "/job-fit",
        json={
            "job_description": "Looking for AI Engineer with FastAPI, LLM, and RAG experience",
            "language": "en",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "fit_score" in data
    assert "fit_label" in data
