from fastapi import FastAPI

from apps.api.routers import (
    alerts_router,
    auth_router,
    health_router,
    ingest_router,
    logs_router,
    services_router,
    uptime_router,
)

app = FastAPI(title="Sentinel API", version="0.1.0")
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(ingest_router)
# The uptime router carries /status, which is deliberately public: it is the
# page you share with people who have no account. Everything below it is gated
# inside those routers, not here.
app.include_router(uptime_router)
app.include_router(logs_router)
app.include_router(services_router)
app.include_router(alerts_router)
