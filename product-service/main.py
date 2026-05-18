from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time, random

app = FastAPI(title="Product Service")

request_count = Counter("product_requests_total", "Total product requests", ["endpoint"])
request_latency = Histogram("product_request_duration_seconds", "Request duration")

PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10},
    {"id": 2, "name": "Mouse", "price": 29.99, "stock": 50},
    {"id": 3, "name": "Keyboard", "price": 79.99, "stock": 30},
    {"id": 4, "name": "Monitor", "price": 349.99, "stock": 15},
    {"id": 5, "name": "Headphones", "price": 149.99, "stock": 25},
]

@app.get("/health")
def health():
    return {"status": "ok", "service": "product-service"}

@app.get("/products")
def get_products():
    start = time.time()
    request_count.labels(endpoint="/products").inc()
    time.sleep(random.uniform(0.01, 0.05))  # simulate small latency
    request_latency.observe(time.time() - start)
    return {"products": PRODUCTS}

@app.get("/products/{product_id}")
def get_product(product_id: int):
    request_count.labels(endpoint="/products/id").inc()
    for p in PRODUCTS:
        if p["id"] == product_id:
            return p
    return {"error": "Product not found"}, 404

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
