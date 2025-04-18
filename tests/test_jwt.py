from fastapi.testclient import TestClient
from api_main import app

client = TestClient(app)

def test_invalid_token():
    response = client.post("/ask", json={"session_id": "x", "question": "x"}, headers={"Authorization": "Bearer wrong"})
    assert response.status_code == 401
