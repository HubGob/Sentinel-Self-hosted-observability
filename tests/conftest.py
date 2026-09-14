import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

import sentinel.models  # noqa: F401  (registers every table on Base.metadata)
from sentinel.database import Base, engine


@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def redis():
    with RedisContainer("redis:7-alpine") as redis:
        yield redis


@pytest.fixture(autouse=True)
async def _truncate_tables():
    """Start every test from an empty database so tests stay order-independent."""
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    yield
