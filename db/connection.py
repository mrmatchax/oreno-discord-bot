import asyncpg
import os

_pool: asyncpg.Pool | None = None


async def create_pool() -> asyncpg.Pool:
    """Create and cache the asyncpg connection pool on bot startup."""
    global _pool
    _pool = await asyncpg.create_pool(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB"),
        min_size=2,
        max_size=10,
    )
    return _pool


def get_pool() -> asyncpg.Pool:
    """Return the shared pool. Must call create_pool() first on startup."""
    if _pool is None:
        raise RuntimeError("Database pool has not been initialized. Call create_pool() first.")
    return _pool


async def close_pool() -> None:
    """Gracefully close the pool on bot shutdown."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
