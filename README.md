# Sentinel

Self-hosted observability for small deployments.

Sentinel collects application logs, processes them into structured events, detects basic operational problems, and exposes them through an API and web dashboard.

## Quick Start

```bash
git clone https://github.com/HubGob/Sentinel-Self-hosted-observability.git
cd sentinel
cp .env.example .env
docker compose up -d
```

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:5173

## Architecture

```
Docker Container → Collector → API → Redis → Worker → PostgreSQL → Alert Engine
                                                          ↓
                                                   REST API ← Dashboard
```

See [docs/architecture.md](docs/architecture.md) for details.

## Development

### Backend

```bash
uv sync --extra dev
uv run fastapi dev apps/api/main.py
uv run python -m apps.worker
uv run pytest
```

### Frontend

```bash
cd web
npm install
npm run dev
```

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /ready | Readiness check |
| POST | /api/v1/ingest | Ingest a log entry |
| GET | /api/v1/logs | List logs (paginated, filterable) |
| GET | /api/v1/services | List services |
| GET | /api/v1/alerts | List alerts (paginated) |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | postgresql+psycopg://sentinel:sentinel@postgres:5432/sentinel | PostgreSQL connection |
| REDIS_URL | redis://redis:6379/0 | Redis connection |
| API_HOST | 0.0.0.0 | API bind address |
| API_PORT | 8000 | API port |
| WORKER_POLL_INTERVAL | 1.0 | Worker poll interval (seconds) |
| WORKER_BATCH_SIZE | 100 | Worker batch size |
| LOG_LEVEL | INFO | Logging level |

## Testing

```bash
uv run pytest                              # All tests
uv run pytest tests/unit/                  # Unit tests only
uv run pytest tests/api/                   # API tests only
uv run pytest tests/integration/           # Integration tests (needs Docker)
```

## Linting and Type Checking

```bash
uv run ruff check .        # Lint
uv run ruff format .       # Format
uv run mypy sentinel/ apps/ # Type check
```

## License

Apache 2.0 - See [LICENSE](LICENSE)
