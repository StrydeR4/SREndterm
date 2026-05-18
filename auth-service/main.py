from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time

app = FastAPI(title="Auth Service")

# Prometheus metrics
login_counter = Counter("auth_login_total", "Total login attempts", ["status"])

# Fake user DB
USERS = {
    "admin": "password123",
    "user1": "pass1",
}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth-service"}

@app.post("/login")
def login(req: LoginRequest):
    if USERS.get(req.username) == req.password:
        login_counter.labels(status="success").inc()
        return {"token": f"fake-token-{req.username}-{int(time.time())}", "username": req.username}
    login_counter.labels(status="failure").inc()
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
