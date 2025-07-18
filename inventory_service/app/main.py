from fastapi import FastAPI
from app.routers import item
from app.utils.metrics import metrics_middleware, metrics_endpoint

app = FastAPI(title="Inventory Service")

app.include_router(item.router)

# Add middleware
app.middleware("http")(metrics_middleware)

# Add /metrics route
app.add_api_route("/metrics", endpoint=metrics_endpoint(), methods=["GET"])


