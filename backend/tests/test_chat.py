from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_endpoint():
    res = client.post("/chat", json={"message": "What AI projects has he built?", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert isinstance(data["sources"], list)
