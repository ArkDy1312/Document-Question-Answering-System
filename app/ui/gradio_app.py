import gradio as gr
import requests
import os
import matplotlib.pyplot as plt
import time
import threading

base_api = os.getenv("API_BASE", "http://localhost:8000")
chat_history = {}

gr.Markdown("""
<style>
.latency-red input { background-color: #ffcccc; color: black; font-weight: bold; }
.latency-orange input { background-color: #fff4cc; color: black; font-weight: bold; }
.latency-green input { background-color: #ccffcc; color: black; font-weight: bold; }
</style>
""")

### --- AUTH HELPERS --- ###
def authenticate(endpoint, username, password):
    url = f"{base_api}/{endpoint}"
    response = requests.post(url, json={"username": username, "password": password})
    if response.status_code == 200:
        return response.json().get("access_token"), None
    return None, response.json().get("detail", "Login failed.")

def signup_user(username, password): return authenticate("signup", username, password)
def login_user(username, password): return authenticate("login", username, password)
def login_admin(username, password): return authenticate("admin-login", username, password)

### --- USER LOGIC --- ###
def ask_question(session_id, question, token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.post(f"{base_api}/ask", json={"session_id": session_id, "question": question}, headers=headers)
        return r.json().get("answer", "No answer returned")
    except Exception as e:
        return f"❌ Error: {e}"

### --- ADMIN LOGIC --- ###
def fetch_admin_metrics(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(f"{base_api}/admin/metrics", headers=headers)
        data = r.json()
        total = str(data["total_queries"])
        today = str(data["today_queries"])
        latency = float(data["avg_latency"])
        color = "green" if latency <= 1500 else "orange" if latency <= 3000 else "red"
        latency_box = gr.Textbox.update(value=f"{latency:.2f} ms", label="Avg Latency", interactive=False, elem_classes=[f"latency-{color}"])
        return total, today, latency_box
    except:
        return "❌", "❌", gr.Textbox.update(value="❌", label="Avg Latency")

def fetch_top_slow(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(f"{base_api}/admin/top-slow", headers=headers)
        data = r.json()
        questions = [q["question"][:30] + "..." for q in data]
        latencies = [q["latency_ms"] for q in data]
        fig, ax = plt.subplots()
        ax.barh(questions, latencies)
        ax.set_xlabel("Latency (ms)")
        ax.set_title("Top Slow Queries")
        return fig
    except:
        return plt.figure()

def fetch_failure_count(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(f"{base_api}/admin/failures", headers=headers)
        return str(r.json().get("failures", 0))
    except:
        return "❌"

def logout(token):
    try:
        requests.post(f"{base_api}/logout", headers={"Authorization": f"Bearer {token}"})
    except:
        pass
    return "", "", "", "👋 Logged out", *show_login_ui()

### --- UI FLOW HELPERS --- ###
def show_user_ui(): return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
def show_admin_ui(): return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
def show_login_ui(): return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)

def handle_user_login(username, password):
    token, error = login_user(username, password)
    if token:
        return token, "user", username, f"✅ Welcome, {username}", *show_user_ui()
    return "", "", "", f"❌ {error}", *show_login_ui()

def handle_signup(username, password):
    token, error = signup_user(username, password)
    if token:
        return token, "user", username, f"✅ Account created for {username}", *show_user_ui()
    return "", "", "", f"❌ {error}", *show_login_ui()

def handle_admin_login(username, password):
    token, error = login_admin(username, password)
    if token:
        return token, "admin", username, f"✅ Welcome Admin {username}", *show_admin_ui()
    return "", "", "", f"❌ {error}", *show_login_ui()

### --- BUILD UI --- ###
with gr.Blocks(title="Document QA Platform") as app:
    token = gr.State("")
    role = gr.State("")
    username = gr.State("")

    # --- USER PANEL ---
    with gr.Group(visible=False) as user_panel:
        gr.Markdown("### 🧠 Ask a Question")
        session_id = gr.Textbox(label="Session ID")
        question = gr.Textbox(label="Your Question")
        answer_output = gr.Textbox(label="Answer", interactive=False)
        ask_btn = gr.Button("Ask")
        logout_btn1 = gr.Button("Logout")

    # --- ADMIN PANEL ---
    with gr.Group(visible=False) as admin_panel:
        gr.Markdown("### 👑 Admin Dashboard")
        with gr.Row():
            total_card = gr.Textbox(label="Total Queries", interactive=False)
            today_card = gr.Textbox(label="Today", interactive=False)
            avg_latency_card = gr.Textbox(label="Avg Latency (ms)", interactive=False)
            failure_card = gr.Textbox(label="Total Failures", interactive=False)

        top_chart = gr.Plot(label="Top Slow Queries")
        auto_refresh = gr.Textbox(value="5", label="Auto Refresh (sec)")
        refresh_btn = gr.Button("🔄 Manual Refresh")
        loading_spinner = gr.Markdown("⏳ Refreshing data...", visible=False)
        logout_btn2 = gr.Button("Logout")

        gr.Markdown("[🔍 FastAPI Docs](http://localhost:8000/docs)")
        gr.Markdown("[📈 Grafana](http://localhost:3000)")
        gr.Markdown("[📡 Prometheus](http://localhost:9090)")
        gr.Markdown("[🧮 Mongo Express](http://localhost:8081)")

    # --- LOGIN PANEL ---
    with gr.Group(visible=True) as login_panel:
        gr.Markdown("### 🔐 Login or Signup")
        user = gr.Textbox(label="Username")
        pwd = gr.Textbox(label="Password", type="password")
        login_btn = gr.Button("Login as User")
        signup_btn = gr.Button("Signup")
        admin_login_btn = gr.Button("Admin Login")
        login_output = gr.Textbox(label="Status", interactive=False)

    # --- Bindings ---
    ask_btn.click(fn=ask_question, inputs=[session_id, question, token], outputs=answer_output)

    login_btn.click(fn=handle_user_login, inputs=[user, pwd],
                    outputs=[token, role, username, login_output, user_panel, admin_panel, login_panel])

    signup_btn.click(fn=handle_signup, inputs=[user, pwd],
                     outputs=[token, role, username, login_output, user_panel, admin_panel, login_panel])

    admin_login_btn.click(fn=handle_admin_login, inputs=[user, pwd],
                          outputs=[token, role, username, login_output, user_panel, admin_panel, login_panel])

    refresh_btn.click(
        fn=lambda t: fetch_admin_metrics(t) + (fetch_top_slow(t), fetch_failure_count(t)),
        inputs=[token],
        outputs=[total_card, today_card, avg_latency_card, top_chart, failure_card]
    )

    logout_btn1.click(fn=logout, inputs=[token], outputs=[token, role, username, login_output, user_panel, admin_panel, login_panel])
    logout_btn2.click(fn=logout, inputs=[token], outputs=[token, role, username, login_output, user_panel, admin_panel, login_panel])

### --- BACKGROUND AUTO REFRESH THREAD --- ###
def background_auto_refresh():
    while True:
        try:
            time.sleep(int(auto_refresh.value))
            if token.value and role.value == "admin":
                loading_spinner.update(visible=True)
                t, d, lbox = fetch_admin_metrics(token.value)
                f = fetch_failure_count(token.value)
                fig = fetch_top_slow(token.value)

                total_card.update(value=t)
                today_card.update(value=d)
                avg_latency_card.update(**lbox)
                failure_card.update(value=f)
                top_chart.update(value=fig)
                loading_spinner.update(visible=False)
        except Exception as e:
            print(f"[Auto Refresh Error] {e}")
            loading_spinner.update(visible=False)
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=background_auto_refresh, daemon=True).start()
    app.launch(server_name="0.0.0.0", server_port=7860)
