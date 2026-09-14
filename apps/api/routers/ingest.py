from fastapi import APIRouter, HTTPException

from sentinel.queue.redis_queue import RedisQueue
from sentinel.schemas.ingest import IngestResponse, LogIngest

router = APIRouter(prefix="/api/v1", tags=["ingest"])
queue = RedisQueue()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_log(log: LogIngest) -> IngestResponse:
    try:
        queue.enqueue(log.model_dump(mode="json"))
        return IngestResponse(accepted=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
