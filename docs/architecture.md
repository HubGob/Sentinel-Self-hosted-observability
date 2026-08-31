# Sentinel Architecture

## Data Flow

```
Docker Container → Collector → API → Redis → Worker → PostgreSQL → Alert Engine
                                                          ↓
                                                   REST API ← Dashboard
```

## Components

### Collector
Reads Docker container logs and sends them to the ingestion API. Runs as a separate service with Docker socket access.

### API
FastAPI application providing:
- `POST /api/v1/ingest` — Log ingestion endpoint
- `GET /api/v1/logs` — Log retrieval with pagination and filters
- `GET /api/v1/services` — Service listing
- `GET /api/v1/alerts` — Alert listing with pagination
- `GET /health` — Health check
- `GET /ready` — Readiness check

### Queue
Redis list-based queue (`LPUSH`/`BRPOP`) buffering ingestion between the API and worker.

### Worker
Polls Redis for new log entries, normalizes them, persists to PostgreSQL, and evaluates alert rules.

### Alert Engine
Threshold-based rules evaluated per service within time windows:
- `error_count > N` — Count of ERROR logs exceeds threshold
- `error_rate > N` — Rate of ERROR logs per second exceeds threshold

### Database

- **services** — Discovered services with last_seen tracking
- **logs** — Normalized log entries with level, timestamp, source
- **alert_rules** — User-defined alert thresholds
- **alerts** — Triggered alert instances with resolution tracking

### Web Dashboard
React application consuming the REST API:
- Services overview
- Log viewer with level filters
- Alert viewer with active/resolved status

## Tech Stack

### Backend
- Python 3.13+
- FastAPI + Pydantic v2
- SQLAlchemy (async) + Alembic
- PostgreSQL + Redis

### Frontend
- React + TypeScript + Vite
- TanStack Query for data fetching
- Tailwind CSS for styling
- Recharts for visualizations

## Deployment

All components deploy via Docker Compose:
- `postgres:16-alpine`
- `redis:7-alpine`
- API container (FastAPI + uvicorn)
- Worker container
- Web container (React + nginx)
