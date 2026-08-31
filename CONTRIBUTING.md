# Contributing to Sentinel

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

```bash
uv sync --extra dev
```

## Code Style

We use Ruff for linting and formatting:

```bash
uv run ruff check .
uv run ruff format .
```

## Testing

```bash
uv run pytest
```

## Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `chore:` Maintenance
