import gradio as gr
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000/ask")
JWT_TOKEN = "secret123"  # Same as in auth.py
chat_history = {}

def ask_question(session_id, question):
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    print("📡 Gradio sending:", API_URL)
    print("🔐 With headers:", headers)

    try:
        response = requests.post(API_URL, json={"session_id": session_id, "question": question}, headers=headers)
        print("✅ Status Code:", response.status_code)
        print("📥 Response:", response.text)
        answer = response.json().get("answer", "No answer in response")
        return f"{answer}"
    except Exception as e:
        print("❌ Request failed:", e)
        return f"Error: {e}"

iface = gr.Interface(
    fn=ask_question,
    inputs=["text", "text"],
    outputs="text",
    title="Document QA",
    description="Ask questions about your uploaded documents. Enter session ID and your question."
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)
