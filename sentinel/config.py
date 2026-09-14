import logging

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Published in the repository, so it is public by definition. It exists so a
# fresh clone runs without configuration; it must never protect a real
# deployment, because anyone could mint valid tokens for it. Kept at 32+ bytes
# so it also satisfies RFC 7518 3.2, the minimum for HMAC-SHA256.
INSECURE_DEFAULT_SECRET = "dev-insecure-secret-change-me-not-for-production"
MINIMUM_SECRET_BYTES = 32


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://sentinel:sentinel@localhost:5432/sentinel"
    redis_url: str = "redis://localhost:6379/0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    worker_poll_interval: float = 1.0
    worker_batch_size: int = 100
    log_level: str = "INFO"
    discord_webhook_url: str | None = None

    jwt_secret: str = INSECURE_DEFAULT_SECRET
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 7

    @model_validator(mode="after")
    def _warn_on_weak_secret(self) -> "Settings":
        if self.jwt_secret == INSECURE_DEFAULT_SECRET:
            logger.warning(
                "JWT_SECRET is the public development default. Anyone can forge tokens "
                "for this deployment; set JWT_SECRET before exposing it to a network."
            )
        elif len(self.jwt_secret.encode("utf-8")) < MINIMUM_SECRET_BYTES:
            logger.warning(
                "JWT_SECRET is under %d bytes, below the RFC 7518 3.2 minimum for "
                "HMAC-SHA256, which weakens every signature this deployment issues.",
                MINIMUM_SECRET_BYTES,
            )
        return self


settings = Settings()
