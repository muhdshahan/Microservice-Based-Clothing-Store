# prometheus_client is official python library for exporting metrics to prometheus
from prometheus_client import Counter, generate_latest
from fastapi import APIRouter, Response

router = APIRouter() # this new route can be included in our mainapp 

# this creates a Prometheus counter metric named "user_created_total" and this should be in snake_case 
# "Total users created" its the help string, shown in Prometheus dashboards and docs
user_created_counter = Counter("user_created_total", "Total users created")

@router.get("/metrics")
async def metrics():
    # generate_latest() returns all metrics our service has collected(as raw Prometheus data)
    return Response(generate_latest(), media_type="text/plain")
