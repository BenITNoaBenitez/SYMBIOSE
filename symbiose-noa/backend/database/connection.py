from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncpg
from config import settings

_pool: asyncpg.Pool | None = None


async def init_db() -> None:
    global _pool
    # asyncpg ne supporte pas le préfixe +asyncpg de SQLAlchemy
    dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    _pool = await asyncpg.create_pool(dsn=dsn, min_size=2, max_size=10)


@asynccontextmanager
async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    if _pool is None:
        raise RuntimeError("Database pool not initialized — init_db() not called")
    async with _pool.acquire() as conn:
        yield conn
