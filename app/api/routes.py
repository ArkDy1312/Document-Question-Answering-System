from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.qa_engine import get_answer
from app.auth.jwt_handler import get_current_user_with_role
from datetime import datetime
from app.db.mongo import  logs
from prometheus_client import REGISTRY

router = APIRouter()

class QuestionRequest(BaseModel):
    session_id: str
    question: str

@router.post("/ask")
async def ask_question(data: QuestionRequest, user=Depends(get_current_user_with_role("user"))):
    """User-only access to RAG question answering."""
    answer = get_answer(data.session_id, data.question)
    # answer = {"answer": "Hello!",
            #   "trace_id": "12345"}
    return answer

@router.get("/admin/metrics")
def get_admin_metrics(admin=Depends(get_current_user_with_role("admin"))):
    total_queries = logs.count_documents({})
    today_count = logs.count_documents({"timestamp": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)}})

    avg_latency = logs.aggregate([
        {"$group": {"_id": None, "avgLatency": {"$avg": "$latency_ms"}}}
    ])
    avg_latency = next(avg_latency, {}).get("avgLatency", 0)

    return {
        "total_queries": total_queries,
        "today_queries": today_count,
        "avg_latency": round(avg_latency, 2)
    }

@router.get("/admin/top-slow")
def get_top_slow_queries(limit: int = 5, admin=Depends(get_current_user_with_role("admin"))):
    logs = db["logs"]
    entries = logs.find().sort("latency_ms", -1).limit(limit)
    return [
        {
            "question": entry["question"],
            "latency_ms": entry["latency_ms"],
            "timestamp": entry["timestamp"].isoformat()
        }
        for entry in entries
    ]


@router.get("/admin/failures")
def get_failure_count(admin=Depends(get_current_user_with_role("admin"))):
    for metric in REGISTRY.collect():
        if metric.name == "qa_failures":
            for sample in metric.samples:
                if sample.name == "qa_failures_total":
                    return {"failures": int(sample.value)}
    return {"failures": 0}