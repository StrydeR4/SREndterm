from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import os, psycopg2, time

app = FastAPI(title="Order Service")

order_counter = Counter("orders_total", "Total orders", ["status"])
error_counter = Counter("order_errors_total", "Total order errors")

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ordersdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        connect_timeout=3
    )

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(50),
                product_id INTEGER,
                quantity INTEGER,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("[ORDER SERVICE] DB initialized successfully")
    except Exception as e:
        print(f"[ORDER SERVICE] DB init failed: {e}")

@app.on_event("startup")
def startup():
    time.sleep(3)  
    init_db()

class OrderRequest(BaseModel):
    user_id: str
    product_id: int
    quantity: int

@app.get("/health")
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "ok", "service": "order-service", "db": "connected"}
    except Exception as e:
        error_counter.inc()
        return {"status": "degraded", "service": "order-service", "db": str(e)}

@app.post("/orders")
def create_order(req: OrderRequest):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (user_id, product_id, quantity) VALUES (%s, %s, %s) RETURNING id",
            (req.user_id, req.product_id, req.quantity)
        )
        order_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        order_counter.labels(status="success").inc()
        return {"order_id": order_id, "status": "pending", "message": "Order created"}
    except Exception as e:
        error_counter.inc()
        order_counter.labels(status="error").inc()
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")

@app.get("/orders")
def list_orders():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, user_id, product_id, quantity, status, created_at FROM orders ORDER BY id DESC LIMIT 20")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {"orders": [
            {"id": r[0], "user_id": r[1], "product_id": r[2],
             "quantity": r[3], "status": r[4], "created_at": str(r[5])}
            for r in rows
        ]}
    except Exception as e:
        error_counter.inc()
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
