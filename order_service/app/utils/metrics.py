from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response, APIRouter

router = APIRouter()

# Prometheus metrics
REQUEST_COUNT = Counter("order_requests_total", "Total number of requests")
REQUEST_LATENCY = Histogram("order_request_duration_seconds", "Request latency")

@router.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
