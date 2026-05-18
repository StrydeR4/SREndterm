from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from datetime import datetime

app = FastAPI(title="Notification Service")

notification_counter = Counter("notifications_total", "Total notifications sent", ["type"])

NOTIFICATIONS = []

class Notification(BaseModel):
    user_id: str
    type: str
    message: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "notification-service"}

@app.post("/notify")
def send_notification(req: Notification):
    notification = {
        "id": len(NOTIFICATIONS) + 1,
        "user_id": req.user_id,
        "type": req.type,
        "message": req.message,
        "sent_at": datetime.now().isoformat(),
        "status": "delivered"
    }
    NOTIFICATIONS.append(notification)
    notification_counter.labels(type=req.type).inc()
    return {"notification_id": notification["id"], "status": "delivered"}

@app.get("/notifications")
def list_notifications():
    return {"notifications": NOTIFICATIONS[-20:]}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)