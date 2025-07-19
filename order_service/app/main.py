from fastapi import FastAPI, Request, HTTPException
from app.utils.metrics import REQUEST_COUNT, REQUEST_LATENCY, router
from app.routers.order import router as order_router
import time
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

# Include routers
app.include_router(order_router)
app.include_router(router)

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    status_code = 500  # Default to internal error status
    
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except HTTPException as http_exc:
        status_code = http_exc.status_code
        raise
    except Exception as exc:
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        raise
    finally:
        # Always record metrics
        process_time = time.time() - start_time
        path = request.url.path
        
        # Standardize path (replace IDs with {id})
        if "/orders/" in path and path.count("/") > 2:
            path = "/orders/{id}"
        
        REQUEST_COUNT.labels(
            method=request.method.lower(),
            path=path,
            status_code=str(status_code)
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=request.method.lower(),
            path=path
        ).observe(process_time)
