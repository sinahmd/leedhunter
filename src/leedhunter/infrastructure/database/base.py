"""
Database base configuration

Provides SQLAlchemy engine, session factory, and declarative base.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from leedhunter.config import get_settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models"""

    pass


def get_engine():
    """Create async SQLAlchemy engine"""
    settings = get_settings()
    return create_async_engine(
        settings.database.url,
        echo=settings.debug,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )


def get_session_factory(engine):
    """Create async session factory"""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


# Global engine and session factory (lazy initialization)
_engine = None
_async_session_factory = None


def _get_engine():
    """Get or create engine"""
    global _engine
    if _engine is None:
        _engine = get_engine()
    return _engine


def _get_session_factory():
    """Get or create session factory"""
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = get_session_factory(_get_engine())
    return _async_session_factory


# Public API
def get_engine_instance():
    """Get the global engine instance"""
    return _get_engine()


def get_session_factory_instance():
    """Get the global session factory instance"""
    return _get_session_factory()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session

    Usage:
        async with get_session() as session:
            # Use session
            pass
    """
    factory = _get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database (create tables)"""
    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections"""
    global _engine, _async_session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None
