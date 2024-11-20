from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.config.config import PG_HOST, PG_PASSWORD, PG_USERNAME

DATABASE_URL = f"postgresql+asyncpg://{PG_USERNAME}:{PG_PASSWORD}@{PG_HOST}/ViewsDB"

ViewBASE = declarative_base()

view_engine = create_async_engine(DATABASE_URL)

_async_session_maker = sessionmaker(
    bind=view_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_views_session() -> AsyncSession:
    async with _async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
