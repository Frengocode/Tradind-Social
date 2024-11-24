from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, validates, DeclarativeBase
from sqlalchemy.ext.declarative import declarative_base
from src.config.config import PG_HOST, PG_PASSWORD, PG_USERNAME
from sqlalchemy import Integer, DateTime
from datetime import datetime



DATABASE_URL = f"postgresql+asyncpg://{PG_USERNAME}:{PG_PASSWORD}@{PG_HOST}/CommentDB"

comment_engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(bind=comment_engine, class_=AsyncSession)


class CommentBase(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, index = True, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow())

    @validates
    def validate_data(self):
        pass


async def get_comment_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
