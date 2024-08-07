from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import asyncio
engine = create_async_engine(
    "postgresql+asyncpg://postgres:123@localhost/hotel_db",
    future = True,
    echo=True
)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, expire_on_commit=True, class_= AsyncSession)
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


