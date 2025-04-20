
from pymongo import MongoClient
import os
from prometheus_client import Counter
from datetime import datetime
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document

# Use 'mongo' — the service name in docker-compose.yml
# Use "mongo" when running in Docker, "localhost" when local
mongo_host = os.getenv("MONGO_HOST", "localhost")
mongo_port = os.getenv("MONGO_PORT", "27017")

client = MongoClient(f"mongodb://{mongo_host}:{mongo_port}/")

db = client["doc_qa"]
collection = db["documents"]

mongo_docs_saved = Counter("mongo_docs_saved", "Number of documents saved to MongoDB")
mongo_entities_saved = Counter("mongo_entities_saved", "Total entities saved")

def save_metadata(filename, chunks, entities=None):
    doc = {
        "filename": filename,
        "chunks": chunks,
        "entities": entities or [],
    }
    collection.insert_one(doc)
    mongo_docs_saved.inc()
    if entities:
        mongo_entities_saved.inc(len(entities))

def log_query(session_id, question, answer, trace_id, latency_ms):
    def serialize_message(msg: BaseMessage):
        return {
            "type": msg.__class__.__name__,
            "content": msg.content
        }

    def serialize_document(doc: Document):
        return {
            "page_content": doc.page_content,
            "metadata": doc.metadata if hasattr(doc, "metadata") else {}
        }

    serialized_answer = {
        "question": answer.get("question"),
        "answer": answer.get("answer"),
        "chat_history": [serialize_message(m) for m in answer.get("chat_history", [])],
        "source_documents": [serialize_document(d) for d in answer.get("source_documents", [])]
    }

    log_entry = {
        "session_id": session_id,
        "question": question,
        "answer": serialized_answer,
        "trace_id": trace_id,
        "latency_ms": latency_ms,
        "timestamp": datetime.utcnow()
    }

    client["doc_qa"]["logs"].insert_one(log_entry)

    