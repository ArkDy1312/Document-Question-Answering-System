from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.api.qa_engine import get_answer
from fastapi.security import OAuth2PasswordBearer
from app.ingest.mongodb_utils import client

router = APIRouter()

class QuestionRequest(BaseModel):
    session_id: str
    question: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
VALID_TOKEN = "secret123"

def verify_token(token: str = Depends(oauth2_scheme)):
    if token != VALID_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.post("/ask")
async def ask_question(data: QuestionRequest, token: str = Depends(verify_token)):
    answer = get_answer(data.session_id, data.question)
    return {"answer": answer}


# @router.get("/logs/top-latency")
# def get_top_slow_queries(limit: int = 5):
#     logs = client["doc_qa"]["logs"].find().sort("latency_ms", -1).limit(limit)
#     return [
#         {
#             "question": log["question"],
#             "latency_ms": log["latency_ms"],
#             "trace_id": log["trace_id"],
#             "timestamp": log["timestamp"]
#         }
#         for log in logs
#     ]


