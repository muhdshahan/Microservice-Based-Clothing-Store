from fastapi import FastAPI, Request
from app.utils.metrics import REQUEST_COUNT, REQUEST_LATENCY
from app.utils.metrics import router as metrics_router
import time
from app.routers.order import router

app = FastAPI()

app.include_router(router)
# ✅ Register Prometheus metrics endpoint
app.include_router(metrics_router)

# ✅ Register global middleware for Prometheus
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    REQUEST_COUNT.inc()
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    REQUEST_LATENCY.observe(duration)
    return response
