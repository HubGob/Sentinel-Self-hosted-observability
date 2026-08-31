from fastapi import APIRouter, HTTPException
from sentinel.schemas.ingest import LogIngest, IngestResponse
from sentinel.queue.redis_queue import RedisQueue

router = APIRouter(prefix="/api/v1", tags=["ingest"])
queue = RedisQueue()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_log(log: LogIngest):
    try:
        queue.enqueue(log.model_dump())
        return IngestResponse(accepted=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
