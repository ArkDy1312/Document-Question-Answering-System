from fastapi.testclient import TestClient
from api_main import app

client = TestClient(app)

def test_ask_route():
    response = client.post("/ask", json={"session_id": "test", "question": "What is this about?"}, headers={"Authorization": "Bearer secret123"})
    assert response.status_code == 200
    assert "answer" in response.json()
