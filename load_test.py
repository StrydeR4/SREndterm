import asyncio
import aiohttp
import time

BASE = "http://localhost"

async def hit(session, url, method="GET", json=None):
    try:
        if method == "POST":
            async with session.post(url, json=json, timeout=aiohttp.ClientTimeout(total=3)) as r:
                return r.status
        else:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as r:
                return r.status
    except:
        return 0

async def load_test():
    print("Starting load test — 60 seconds, 20 concurrent users")
    print("Watch Grafana at http://localhost:3001\n")

    start = time.time()
    total = 0
    errors = 0

    async with aiohttp.ClientSession() as session:
        while time.time() - start < 60:
            tasks = []
            for i in range(20):
                tasks += [
                    hit(session, f"{BASE}/api/products/products"),
                    hit(session, f"{BASE}/api/auth/health"),
                    hit(session, f"{BASE}/api/orders/orders"),
                    hit(session, f"{BASE}/api/users/users"),
                    hit(session, f"{BASE}/api/orders/orders", method="POST",
                        json={"user_id": f"loadtest_user_{i}", "product_id": (i % 5) + 1, "quantity": 1}),
                ]

            results = await asyncio.gather(*tasks)
            total += len(results)
            errors += results.count(0) + results.count(503)

            elapsed = int(time.time() - start)
            print(f"[{elapsed:>3}s] Requests: {total} | Errors: {errors} | RPS: {total // max(elapsed,1)}")
            await asyncio.sleep(1)

    print(f"\nDone. Total: {total} requests, {errors} errors ({100*errors//total}% error rate)")

if __name__ == "__main__":
    asyncio.run(load_test())