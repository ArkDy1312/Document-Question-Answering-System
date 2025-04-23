from fastapi import APIRouter, Depends, Form, UploadFile, File
from pydantic import BaseModel
import os
from typing import Optional
from datetime import datetime
from prometheus_client import REGISTRY
from app.api.qa_engine import get_answer
from app.auth.jwt_handler import get_current_user_with_role
from datetime import datetime
from app.db.mongo import logs

router = APIRouter()

class QuestionRequest(BaseModel):
    username: str
    session_id: str
    question: str
    upload_dir: Optional[str] = None

@router.post("/ask")
async def ask_question(data: QuestionRequest, user=Depends(get_current_user_with_role("user"))):
    """User-only access to RAG question answering."""
    answer = await get_answer(data.username, data.session_id, data.question, data.upload_dir)
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
    entries = logs.find().sort("latency_ms", -1).limit(limit)
    return [
        {
            "question": entry["question"],
            "latency_ms": entry["latency_ms"],
            "timestamp": entry["timestamp"].isoformat()
        }
        for entry in entries
    ]


@router.post("/store")
async def embed_file(
    file: UploadFile = File(...),
    username: str = Form(...),
    session_id: str = Form(...)
):

    # Save the uploaded file
    temp_upload_dir = f"data/temp_{username}/{session_id}"
    os.makedirs(temp_upload_dir, exist_ok=True)
    file_path = os.path.join(temp_upload_dir, file.filename)
    raw_file_bytes = await file.read()  # Read file bytes
    # Save the raw file bytes to a temporary file
    with open(file_path, "wb") as f:
        f.write(raw_file_bytes)

    return {"upload_dir": temp_upload_dir}
        