"""
Database Session and Models
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.engine import make_url
from app.core.config import settings


def _async_url(url: str) -> str:
    parsed = make_url(url)
    if parsed.get_backend_name() not in {"postgres", "postgresql"}:
        if parsed.drivername == "sqlite":
            return parsed.set(drivername="sqlite+aiosqlite").render_as_string(
                hide_password=False
            )
        return url

    query = dict(parsed.query)
    sslmode = query.pop("sslmode", None)
    if sslmode and "ssl" not in query:
        query["ssl"] = sslmode
    return parsed.set(
        drivername="postgresql+asyncpg",
        query=query,
    ).render_as_string(hide_password=False)


# Async engine
engine = create_async_engine(
    _async_url(settings.DATABASE_URL),
    echo=settings.APP_ENV == "dev",
    future=True,
)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)