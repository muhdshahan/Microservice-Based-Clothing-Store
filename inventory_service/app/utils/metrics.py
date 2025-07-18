# app/utils/metrics.py

from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    "request_count", "Total HTTP requests", ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "request_latency_seconds", "Latency of HTTP requests", ["method", "endpoint"]
)

# Middleware to collect metrics
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    REQUEST_LATENCY.labels(request.method, request.url.path).observe(process_time)
    REQUEST_COUNT.labels(request.method, request.url.path, str(response.status_code)).inc()

    return response

# /metrics endpoint
def metrics_endpoint():
    def handler():
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)
    return handler
