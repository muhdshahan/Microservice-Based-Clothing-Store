# app/utils/metrics.py
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import re

# Define Prometheus metrics with standardized label names
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
    """Convert URL paths to consistent metric-friendly format"""
    # Replace all numbers with {id}
    path = re.sub(r"/\d+", "/{id}", path)
    # Replace multiple slashes with single slash
    path = re.sub(r"/+", "/", path)
    # Remove trailing slash
    path = path.rstrip("/")
    return path or "/"

async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = None
    status_code = 500  # Default to 500 if something fails
    
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        # Create a response object if none exists
        if response is None:
            response = Response(
                content="Internal Server Error",
                status_code=status_code
            )
        raise e
    finally:
        process_time = time.time() - start_time
        sanitized_path = sanitize_path(request.url.path)
        
        # Safe metric recording (response is guaranteed to exist)
        REQUEST_LATENCY.labels(
            method=request.method.lower(),
            path=sanitized_path
        ).observe(process_time)
        
        REQUEST_COUNT.labels(
            method=request.method.lower(),
            path=sanitized_path,
            status_code=str(status_code)    # Use the pre-defined status_code
        ).inc()

    return response

def metrics_endpoint():
    async def handler():
        data = generate_latest()
        return Response(
            content=data,
            media_type=CONTENT_TYPE_LATEST,
            headers={"Cache-Control": "no-cache"}
        )
    return handler