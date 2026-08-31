from fastapi import FastAPI
from apps.api.routers import health_router

app = FastAPI(title="Sentinel API", version="0.1.0")
app.include_router(health_router)
