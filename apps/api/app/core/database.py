"""
MUSNAD AI - Database Configuration
Uses SQLAlchemy async with PostgreSQL + pgvector extension.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_async_db_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


db_url = get_async_db_url(settings.DATABASE_URL)
engine_kwargs = {"echo": settings.APP_DEBUG}
if "sqlite" not in db_url:
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
    })

engine = create_async_engine(db_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    global engine, AsyncSessionLocal
    try:
        async with engine.begin() as conn:
            if "postgresql" in str(engine.url):
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.run_sync(Base.metadata.create_all)
            logger.info("database_initialized", dialect=engine.dialect.name)
    except Exception as e:
        logger.warning("postgres_unavailable_fallback_to_sqlite", error=str(e))
        sqlite_url = "sqlite+aiosqlite:///./musnad_ai.db"
        engine = create_async_engine(sqlite_url, echo=settings.APP_DEBUG)
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database_initialized_with_sqlite_fallback", db_path="./musnad_ai.db")


async def check_db_health() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        return False
