from fastapi import FastAPI
from apps.api.routers import health_router, ingest_router, logs_router, services_router, alerts_router

app = FastAPI(title="Sentinel API", version="0.1.0")
app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(logs_router)
app.include_router(services_router)
app.include_router(alerts_router)
