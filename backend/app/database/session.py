"""Database session management."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.config import settings

# Base class for declarative models
Base = declarative_base()

# Create async engine
engine: AsyncEngine = create_async_engine(
    settings.async_database_url,
    echo=settings.db_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,
)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize database - create tables.

    Note: In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        # Import all models to ensure they're registered
        from app.database import models  # noqa: F401

        # Create tables (only for development)
        if settings.debug:
            await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get database session.

    Yields:
        AsyncSession: Database session
    """
    async with async_session_maker() as session:
        yield session
