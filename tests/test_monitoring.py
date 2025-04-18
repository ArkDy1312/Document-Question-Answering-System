import requests

# --- Test: FastAPI metrics route
def test_metrics_endpoint():
    r = requests.get("http://localhost:8000/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text

# --- Test: Trace-enhanced answer call
def test_qa_with_trace():
    headers = {"Authorization": "Bearer secret123"}
    payload = {"session_id": "test", "question": "What is LangChain?"}
    r = requests.post("http://localhost:8000/ask", json=payload, headers=headers)
    data = r.json()
    assert "answer" in data
    assert "trace_id" in data

# --- Test: Mongo log API
def test_top_latency_log():
    r = requests.get("http://localhost:8000/logs/top-latency?limit=3")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
