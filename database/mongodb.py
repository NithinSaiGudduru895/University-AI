from datetime import datetime, timezone
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB

client = None
db = None

def init_db():
    global client, db
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    client.admin.command("ping")
    db = client[MONGO_DB]
    db.chats.create_index("created_at")

def save_chat(university, question, answer):
    if db is None:
        init_db()
    db.chats.insert_one({
        "university": university,
        "question": question,
        "answer": answer,
        "created_at": datetime.now(timezone.utc)
    })

def get_recent_chats(limit=20):
    if db is None:
        init_db()
    rows = db.chats.find(
        {},
        {"_id": 0, "university": 1, "question": 1, "answer": 1, "created_at": 1}
    ).sort("created_at", -1).limit(limit)
    out = []
    for r in rows:
        if r.get("created_at"):
            r["created_at"] = r["created_at"].isoformat()
        out.append(r)
    return out
