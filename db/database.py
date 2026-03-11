"""
TrainRadar - Database Connection Manager
-----------------------------------------
Manages the connection pool to TimescaleDB.
Use get_db_session() whenever you need to read or write to the database.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

# These are module-level variables — created once and reused
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker | None = None


def get_engine() -> AsyncEngine:
    """
    Creates the database engine (connection pool).
    Only created once — reused every time after that.
    """
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            pool_size=5,          # keep 5 connections open
            max_overflow=10,      # allow 10 extra connections if needed
            pool_pre_ping=True,   # check connection is alive before using it
            echo=False,           # set True to see all SQL in terminal
        )
        logger.info("database.engine_created")
    return _engine


def get_session_factory() -> async_sessionmaker:
    """
    Creates a session factory.
    A session is like a conversation with the database —
    you open it, do some work, then close it.
    """
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _session_factory


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Use this in your code whenever you need the database.

    Example:
        async with get_db_session() as session:
            session.add(some_object)

    It automatically commits on success and rolls back on error.
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error("database.session_error", error=str(exc))
            raise


async def close_engine() -> None:
    """
    Call this when the app shuts down to close all connections cleanly.
    """
    global _engine
    if _engine is not None:
        await _engine.dispose()
        logger.info("database.engine_closed")
        _engine = None