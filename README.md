# Sentinel

Self-hosted observability for small deployments.

## Quick Start

```bash
git clone https://github.com/HubGob/Sentinel-Self-hosted-observability.git
cd sentinel
cp .env.example .env
docker compose up -d
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Dashboard: http://localhost:5173

## Development

```bash
uv sync --extra dev
uv run fastapi dev apps/api/main.py
uv run python -m apps.worker
uv run pytest
```

## License

Apache 2.0
