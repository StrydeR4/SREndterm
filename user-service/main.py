from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from datetime import datetime

app = FastAPI(title="User Service")

user_counter = Counter("user_actions_total", "Total user actions", ["action"])

USERS = {
    "admin": {"id": 1, "username": "admin", "email": "admin@example.com", "role": "admin"},
    "user1": {"id": 2, "username": "user1", "email": "user1@example.com", "role": "user"},
}

# Simple in-memory chat
MESSAGES = []

class Message(BaseModel):
    from_user: str
    to_user: str
    content: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "user-service"}

@app.get("/users")
def get_users():
    user_counter.labels(action="list").inc()
    return {"users": list(USERS.values())}

@app.get("/users/{username}")
def get_user(username: str):
    user_counter.labels(action="get").inc()
    if username in USERS:
        return USERS[username]
    return {"error": "User not found"}

@app.post("/messages")
def send_message(msg: Message):
    user_counter.labels(action="message").inc()
    entry = {
        "id": len(MESSAGES) + 1,
        "from": msg.from_user,
        "to": msg.to_user,
        "content": msg.content,
        "timestamp": datetime.now().isoformat()
    }
    MESSAGES.append(entry)
    return {"status": "sent", "message": entry}

@app.get("/messages")
def get_messages():
    return {"messages": MESSAGES[-20:]}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
