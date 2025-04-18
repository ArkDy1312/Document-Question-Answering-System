import requests
import time

API = "http://localhost:8000/ask"
headers = {"Authorization": "Bearer secret123"}

def test_latency_and_logging():
    for _ in range(5):
        payload = {"session_id": "synthetic-latency", "question": "Slow query test"}
        start = time.perf_counter()
        r = requests.post(API, json=payload, headers=headers)
        latency = (time.perf_counter() - start) * 1000
        print(f"Latency: {latency:.2f} ms | Trace ID: {r.json().get('trace_id')}")
        assert r.status_code == 200
        time.sleep(2)
