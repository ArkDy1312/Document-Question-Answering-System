
# 📄 Document Question Answering System (with Knowledge Graph + RAG)

An open-source, production-ready **Document QA Platform** with:

✅ RAG (Retrieval-Augmented Generation)  
✅ Knowledge Graph Tools  
✅ Admin Dashboard + User Auth  
✅ Monitoring + Feedback Loop  
✅ MLOps with Airflow, MLflow, Prometheus, Docker

---

## 🚀 Highlights

| Module             | Status             | Notes                                                          |
|--------------------|--------------------|----------------------------------------------------------------|
| 🔍 RAG QA Engine     | ✅ Done           | LangChain + FAISS + HuggingFace                                |
| 📦 Ingestion         | ✅ Done           | PDF/TXT parsing, chunking, NER, metadata saved to MongoDB      |
| 🧠 Agent Tools       | 🔜 To be added    | Summarizer, Graph Lookup, Entity Extractor (LangGraph agent)   |
| 🔐 Auth & Roles      | ✅ Done           | Admin/User login & signup (JWT), token blacklist, session mgmt |
| 💬 Gradio UI         | ✅ Done           | Multi-panel UI (QA (User) + Admin Dashboard)                   |
| 📊 Monitoring        | ✅ Done           | Prometheus, Grafana, OpenTelemetry                             |
| ⏱️ Log Scheduler     | ✅ Done           | Airflow DAG to export logs daily to `logs_archive_YYYYMMDD`    |
| 🧪 Feedback Loop     | 🟡 In Progress    | Thumbs up/down, `/feedback` endpoint to be added               |
| 🧬 Fine-Tuning (LoRA)| 🟡 In Progress    | Model scoring + retrain DAG planned                            |
| 🧪 Evaluation        | 🔜 Planned        | BLEU/ROUGE scripts prepped, PDF export next                    |
| 📈 MLflow Registry   | 🔜 Planned        | Ready for versioning + promotion of fine-tuned models          |
| 🔁 CI/CD (GH Actions)| 🔜 Planned        | Testing, build, DAG trigger pipeline                           |

---

## 📂 Project Structure

```
app/
├── api/          # FastAPI routes: QA engine, admin endpoints
├── auth/         # JWT, signup/login, token blacklist
├── ingest/       # File parser, chunker, embedder, NER
├── db/           # Mongo bootstrap + logging
├── dags/         # Airflow DAGs: export_logs, fine_tune (WIP)
├── monitoring/   # Prometheus, Grafana, OpenTelemetry config
├── ml/           # LoRA fine-tuning, eval, model scoring
├── ui/           # Gradio interface (User + Admin panels)
```

---

## 🖥️ Interfaces

| Tool            | URL                          |
|------------------|-------------------------------|
| Gradio UI        | `http://localhost:7860`       |
| FastAPI Docs     | `http://localhost:8000/docs`  |
| Mongo Express    | `http://localhost:8081`       |
| Prometheus       | `http://localhost:9090`       |
| Grafana          | `http://localhost:3000`       |
| MLflow           | `http://localhost:5000`       |
| Airflow UI       | `http://localhost:8080`       |

---

## 📦 Component Overview

### ✅ 1. **User Interface (UI)**
- **Gradio Frontend**
  - User Login / Signup
  - Document upload
  - Ask questions
  - Admin Dashboard (metrics, logs, feedback, retrain trigger)

---

### ✅ 2. **FastAPI Backend**
- Handles:
  - Auth (JWT)
  - Upload endpoints
  - QA routes (`/ask`)
  - Admin routes (`/admin/metrics`, `/admin/top-slow`, `/logout`)

---

### ✅ 3. **Document Ingestion Pipeline**
- Parses PDF/TXT via PyMuPDF
- Chunks documents (LangChain)
- Embeds using HuggingFace model
- Saves:
  - Chunks to FAISS
  - Metadata + NER entities to MongoDB

---

### ✅ 4. **RAG QA Engine**
- Uses LangChain's ConversationalRetrievalChain
- FAISS-based retriever
- HuggingFace QA model (TeapotLLM)
- Supports memory, prompt template
- Logs trace_id, latency, chat history to Mongo

---

### 🔜 5. **LangChain Agent**
- Tools (planned):
  - Summarizer
  - Entity Explorer
  - Graph Lookup (Neo4j)
- Agent auto-routes queries using `zero-shot-react-description`

---

### 🟡 6. **Feedback Loop & Fine-Tune**
- Feedback storage in Mongo
- Airflow DAG to export logs ✅
- Eval (BLEU/ROUGE) & LoRA fine-tuning (planned)
- MLflow model promotion (in progress)

---

### 🟡 7. **Monitoring**
- Prometheus (custom metrics) ✅
- Grafana (auto-refresh dashboard) ✅
- OpenTelemetry (trace context) ✅
- 🟡 Alerts:
  - High latency
  - Downvote spike
  - Retrain failure (to be wired)

---

### 🔜 8. **CI/CD**
- GitHub Actions (planned):
  - Run tests
  - Build Docker
  - Trigger Airflow retrain
- MLflow model registry ✅
- DVC integration (setup ready)

---

## 📈 Data Flow

1. Upload → Parse → Chunk → Embed
2. Store:
    - Embeddings → FAISS
    - Metadata → Mongo
3. Ask Question → Retrieve → Answer via LLM
4. Log (QA + metrics + trace)
5. Admin can:
    - See metrics
    - Export logs (Airflow)
6. CI/CD handles testing, model promotions, DAG triggers (planned)

---

## ✅ Security & Roles

| Role     | Permissions                               |
|----------|--------------------------------------------|
| Admin    | View metrics, retrain model, view logs     |
| User     | Ask questions, upload, see history         |


---

## 📊 Admin Dashboard Metrics

- Live Total Queries, Today's Queries, Failures
- Auto-refresh every X seconds
- Color-coded Latency Alerts (Green/Orange/Red)
- Top N slowest queries bar chart
- Links to FastAPI/Grafana/Prometheus

---

## 🛠 Airflow Pipelines

| DAG                  | Schedule       | Description                                  |
|----------------------|----------------|----------------------------------------------|
| `export_logs_daily`  | Daily @ 00:00  | Backs up QA logs to new Mongo collection     |
| `retrain_lora`       | 🟡 Planned      | Trigger LoRA fine-tune on recent feedback    |

---

## 🔁 Feedback Loop (Next)

| Feature            | Status       |
|--------------------|--------------|
| 👍👎 Voting UI      | 🔜 To be added in Gradio |
| Feedback API       | 🟡 Planned   |
| Log filtering      | 🟡 DAG-ready |
| LoRA retraining    | 🟡 DAG-ready |
| Model eval/compare | ✅ Eval scripts set |

---

## 📦 Dev Tools

- Docker Compose for all services
- Airflow for orchestration
- Prometheus + Grafana for monitoring
- MongoDB + Mongo Express for DB + Admin
- MLflow for experiment tracking

---

## 🗃️ Tech Stack

| Layer        | Tool                     |
|--------------|--------------------------|
| UI           | Gradio                   |
| Backend      | FastAPI                  |
| QA/RAG       | LangChain + HF           |
| DB           | MongoDB                  |
| Embed Store  | FAISS                    |
| Tracing      | OpenTelemetry            |
| Logs/Alerts  | Prometheus + Grafana     |
| Training     | LoRA + Transformers      |
| Workflow     | Apache Airflow           |
| MLOps        | DVC + MLflow             |
| CI/CD        | GitHub Actions (Planned) |

---

## 📋 To-Do / Next Steps

- [ ] Add feedback voting button in Gradio
- [ ] Wire `/feedback` API endpoint
- [ ] DAG: LoRA fine-tuning pipeline from logs
- [ ] Model scoring → MLflow promotion logic
- [ ] Eval → PDF download from admin panel
- [ ] GitHub Actions: CI + Auto-redeploy
- [ ] LangChain Agent Tool integration (Summarizer, Graph, Entity tools)
- [ ] Optional: Neo4j visualization in UI
- [ ] Optional: Grafana alerts on failure