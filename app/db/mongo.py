
from pymongo import MongoClient
import os
from prometheus_client import Counter
from datetime import datetime
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document
from bson.binary import Binary
from app.auth.security import hash_password

# Use 'mongo' — the service name in docker-compose.yml
# Use "mongo" when running in Docker, "localhost" when local
mongo_host = os.getenv("MONGO_HOST", "localhost")
mongo_port = os.getenv("MONGO_PORT", "27017")

client = MongoClient(f"mongodb://{mongo_host}:{mongo_port}/")

db = client["doc_qa"]
collection = db["documents"]
users_docs_collection = db["user_documents"]
logs = db["logs"]
users_collection = db["users"]
admins_collection = db["admins"]
blacklist_collection = db["blacklisted_tokens"]
blacklist_collection.create_index("exp", expireAfterSeconds=1000)  # Optional TTL cleanup

mongo_docs_saved = Counter("mongo_docs_saved", "Number of documents saved to MongoDB")
mongo_entities_saved = Counter("mongo_entities_saved", "Total entities saved")
mongo_users = Counter("mongo_users", "Total Number of Users")

# --- Bootstrap admin credentials ---
DEFAULT_ADMIN_USERNAME = os.getenv("MONGO_DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("MONGO_DEFAULT_ADMIN_PASSWORD", "admin123")

# Insert default admin only if not present
if not admins_collection.find_one({"username": DEFAULT_ADMIN_USERNAME}):
    admins_collection.insert_one({
        "username": DEFAULT_ADMIN_USERNAME,
        "hashed_password": hash_password(DEFAULT_ADMIN_PASSWORD),
        "role": "admin",
        "token": ""  # will be generated on login
    })
    print(f"[BOOTSTRAP] ✅ Admin user '{DEFAULT_ADMIN_USERNAME}' created.")
else:
    print(f"[BOOTSTRAP] 🟢 Admin user '{DEFAULT_ADMIN_USERNAME}' already exists.")

def save_metadata(filename, chunks, entities=None, username=None, session_id=None, upload_time=None):
    if username and session_id:
        doc = {
        "filename": filename,
        "username": username,
        "session_id": session_id,
        "upload_time": upload_time,
        }
        users_docs_collection.insert_one(doc)
    else:
        doc = {
            "filename": filename,
            "chunks": chunks,
            "entities": entities or [],
        }
        collection.insert_one(doc)
    
    # Increment the document count
    mongo_docs_saved.inc()
    if entities:
        mongo_entities_saved.inc(len(entities))

def log_query(username, session_id, question, answer, trace_id, latency_ms):
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
        "username": username,
        "session_id": session_id,
        "question": question,
        "answer": serialized_answer,
        "trace_id": trace_id,
        "latency_ms": latency_ms,
        "timestamp": datetime.utcnow()
    }

    logs.insert_one(log_entry)

    