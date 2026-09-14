# Sentinel

Self-hosted observability for small deployments.

Sentinel collects application logs, processes them into structured events, detects basic operational problems, and exposes them through an API and web dashboard.

## Quick Start

```bash
git clone https://github.com/HubGob/Sentinel-Self-hosted-observability.git
cd sentinel
cp .env.example .env

# Set a real signing secret. The default in .env.example is published in this
# repository, so anyone could forge tokens for a deployment that kept it.
openssl rand -hex 32   # paste the output into JWT_SECRET in .env

docker compose up -d

# Create the first account — the dashboard needs one to sign in.
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"at-least-8-characters"}'
```

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:5173 (sign in with the account above)
- **Public status page**: http://localhost:5173/status (no login required)

Everything under the dashboard requires a token. `/status`, `/health`, `/ready`
and the agent's ingest endpoint stay open, so the status page can still be
shared with people who have no account.

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

`Auth` marks an endpoint that requires `Authorization: Bearer <access_token>`.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /health | — | Health check |
| GET | /ready | — | Readiness check |
| POST | /api/v1/auth/register | — | Create an account, returns tokens |
| POST | /api/v1/auth/login | — | Exchange credentials for tokens |
| POST | /api/v1/auth/refresh | — | Exchange a refresh token for a new access token |
| POST | /api/v1/ingest | — | Ingest a log entry (used by the agent and collector) |
| GET | /api/v1/status | — | Public uptime summary for the status page |
| GET | /api/v1/logs | yes | List logs (paginated, filterable) |
| GET | /api/v1/services | yes | List services |
| GET | /api/v1/alerts | yes | List alerts (paginated) |

Access tokens live 15 minutes; refresh tokens live 7 days. The dashboard
refreshes and retries automatically, so this is only visible to API clients.

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
| JWT_SECRET | development default | Signing secret — **set this** (see Quick Start) |
| JWT_ALGORITHM | HS256 | Signing algorithm |
| ACCESS_TOKEN_TTL_MINUTES | 15 | Access token lifetime |
| REFRESH_TOKEN_TTL_DAYS | 7 | Refresh token lifetime |

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
