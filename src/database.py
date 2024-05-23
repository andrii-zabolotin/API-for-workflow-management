from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from typing import AsyncGenerator

from src.config import settings

# Creating a connection to the database
engine = create_async_engine(settings.db_url)

# Creating a session factory for interacting with the database
SessionLocal = sessionmaker(engine, class_=AsyncSession, autocommit=False, autoflush=False, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Function for providing an asynchronous session.

    Yields:
        AsyncSession: An asynchronous session instance.
    """
    async with SessionLocal() as session:
        yield session
