from typing import Annotated, AsyncIterator

from fastapi import Depends
from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from core.config import settings

async_engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True, )


AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    future=True,
)


class BaseModel(DeclarativeBase):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    create_at = Column(DateTime(timezone=True), server_default=func.now())
    last_update = Column(DateTime(timezone=True), server_onupdate=func.now())


async def get_session() -> AsyncIterator[async_sessionmaker]:
    yield AsyncSessionLocal


AsyncSession = Annotated[async_sessionmaker, Depends(get_session)]
