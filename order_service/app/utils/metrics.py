from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response, APIRouter
import re

router = APIRouter()

REQUEST_COUNT = Counter(
    "http_requests_total",  
    "Total HTTP requests",
    ["method", "path", "status_code"]  
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",  
    "Latency of HTTP requests",
    ["method", "path"],  
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0]  
)

def sanitize_path(path: str) -> str:
    """EXACT same implementation as used in middleware"""
    path = re.sub(r"/\d+", "/{id}", path)  # Replace IDs with {id}
    path = re.sub(r"/+", "/", path)        # Normalize slashes
    return path.rstrip("/") or "/"          # Handle root path

@router.get("/metrics")
async def metrics():
    """Keep this endpoint simple as in your original"""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )