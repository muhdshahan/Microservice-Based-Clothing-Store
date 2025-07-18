from fastapi import FastAPI
from app.routers import user
from app.metrics import prometheus_metrics

app = FastAPI(title= "User Service")

app.include_router(user.router)
app.include_router(prometheus_metrics.router)