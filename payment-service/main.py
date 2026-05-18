from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time, random

app = FastAPI(title="Payment Service")

payment_counter = Counter("payments_total", "Total payments", ["status"])
payment_latency = Histogram("payment_duration_seconds", "Payment processing duration")

class PaymentRequest(BaseModel):
    order_id: int
    user_id: str
    amount: float

PAYMENTS = []

@app.get("/health")
def health():
    return {"status": "ok", "service": "payment-service"}

@app.post("/payments")
def process_payment(req: PaymentRequest):
    start = time.time()
    time.sleep(random.uniform(0.05, 0.2))
    if random.random() < 0.95:
        payment = {
            "id": len(PAYMENTS) + 1,
            "order_id": req.order_id,
            "user_id": req.user_id,
            "amount": req.amount,
            "status": "success",
            "timestamp": time.time()
        }
        PAYMENTS.append(payment)
        payment_counter.labels(status="success").inc()
        payment_latency.observe(time.time() - start)
        return {"payment_id": payment["id"], "status": "success", "amount": req.amount}
    else:
        payment_counter.labels(status="failed").inc()
        raise HTTPException(status_code=402, detail="Payment declined")

@app.get("/payments")
def list_payments():
    return {"payments": PAYMENTS[-20:]}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)