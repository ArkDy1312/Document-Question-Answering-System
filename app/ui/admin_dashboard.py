import gradio as gr
import requests
import os

# --- CONFIG ---
API_BASE = os.getenv("API_URL", "http://localhost:8000")
PROMETHEUS_API = os.getenv("PROMETHEUS_API", "http://localhost:9090/api/v1/query")

# --- LOAD TOP SLOW QUERIES ---
def load_top_slow_queries(n=5):
    resp = requests.get(f"{API_BASE}/logs/top-latency?limit={n}")
    data = resp.json()
    return [(d["question"], d["latency_ms"], d["trace_id"], d["timestamp"]) for d in data]

# --- LOAD LIVE LATENCY FROM PROMETHEUS ---
def get_live_latency():
    query = 'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[1m])) by (le))'
    r = requests.get(PROMETHEUS_API, params={"query": query}).json()
    latency = r["data"]["result"][0]["value"][1] if r["data"]["result"] else "N/A"
    return f"🕒 P95 latency: {round(float(latency)*1000, 2)} ms"

# --- GRADIO UI ---
def admin_panel():
    with gr.Blocks() as demo:
        gr.Markdown("## 🧠 Document QA Admin Dashboard")
        latency_box = gr.Textbox(label="Live Latency", interactive=False)
        refresh_btn = gr.Button("Refresh Latency")

        with gr.Row():
            n_slider = gr.Slider(minimum=1, maximum=20, value=5, label="Top N Queries")
            query_table = gr.Dataframe(headers=["Question", "Latency (ms)", "Trace ID", "Timestamp"])

        # Bind events
        refresh_btn.click(fn=get_live_latency, outputs=latency_box)
        n_slider.change(fn=load_top_slow_queries, inputs=n_slider, outputs=query_table)

    return demo

if __name__ == "__main__":
    admin_panel().launch(server_name="0.0.0.0", server_port=7861)
