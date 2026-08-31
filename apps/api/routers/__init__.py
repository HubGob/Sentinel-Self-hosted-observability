from apps.api.routers.health import router as health_router
from apps.api.routers.ingest import router as ingest_router
from apps.api.routers.logs import router as logs_router
from apps.api.routers.services import router as services_router
from apps.api.routers.alerts import router as alerts_router

__all__ = ["health_router", "ingest_router", "logs_router", "services_router", "alerts_router"]
