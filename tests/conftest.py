from typing import AsyncGenerator
import asyncio
from httpx import AsyncClient
import pytest
from sqlalchemy import NullPool, select, insert, and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from src.config import settings
from src.database import get_async_session
from src.main import app
from src.models import Base, WorkFlow, StartNode, MessageNode, ConditionNode, EndNode, Status

# Database
# Creates an asynchronous SQLAlchemy engine for the test database using the URL from the settings object.
test_engine = create_async_engine(settings.db_url, poolclass=NullPool)
# SQLAlchemy session factory using the created test_engine.
test_SessionLocal = sessionmaker(test_engine, class_=AsyncSession, autocommit=False, autoflush=False, expire_on_commit=False)
# Binds the SQLAlchemy models' metadata to the test_engine.
Base.metadata.bind = test_engine


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields:
        AsyncSession: An asynchronous session.
    """
    async with test_SessionLocal() as session:
        yield session


# overrides the dependency get_async_session in the app object with the asynchronous function.
app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    """
    Prepares the database before running tests in the session scope.

    Yields:
        None
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Setup
@pytest.fixture(scope="session")
def event_loop(request):
    """
    Fixture for providing an event loop for the session scope.

    Args:
        request: The request object.

    Yields:
        asyncio.AbstractEventLoop: An event loop.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client():
    """
    Fixture for providing a test client for the session scope.

    Yields:
        TestClient: A test client instance.
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture for providing an asynchronous test client for the session scope.

    Yields:
        AsyncClient: An asynchronous test client instance.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture for providing an asynchronous session for the function scope.

    Yields:
        AsyncSession: An asynchronous session instance.
    """
    async with test_SessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def get_or_create_workflow_id() -> int:
    """
    Fixture for providing a workflow object for the function scope.

    Returns:
        WorkFlow: Model instance.
    """
    async with test_SessionLocal() as session:
        stmt = select(WorkFlow).where(WorkFlow.id == 1)
        result = await session.execute(stmt)
        workflow = result.scalar_one_or_none()
        if workflow:
            return workflow.id
        stmt = insert(WorkFlow).returning(WorkFlow.id)
        result = await session.execute(stmt)
        workflow_id = result.scalar_one()
        await session.commit()
        return workflow_id


async def get_or_create_node_id(node_model, values: dict = None) -> int:
    """
    Get the ID of an existing node or create a new one if it doesn't exist.

    Params:
        node_model: The SQLAlchemy model class representing the node.
        values: A dictionary of field names and values used to create the node.

    Returns:
        int: The ID of the existing or newly created node.
    """
    async with test_SessionLocal() as session:
        stmt = select(node_model).where(and_(*[getattr(node_model, key) == value for key, value in values.items()]))
        result = await session.execute(stmt)
        node = result.scalar_one_or_none()
        if node:
            return node.id

        node = node_model(**values)
        session.add(node)
        await session.commit()
        return node.id


@pytest.fixture(scope="function")
async def get_or_create_start_node_id(get_or_create_workflow_id: int) -> int:
    """
    Fixture for providing a StartNode object for the function scope.

    Returns:
        StartNode: Model instance.
    """
    payload = {
        "workflow_id": get_or_create_workflow_id
    }
    return await get_or_create_node_id(node_model=StartNode, values=payload)


@pytest.fixture(scope="function")
async def get_or_create_message_node_id(get_or_create_workflow_id: int) -> int:
    """
    Fixture for providing a MessageNode object for the function scope.

    Returns:
        MessageNode: Model instance.
    """
    payload = {
        "status": Status.SENT,
        "message": "Hello world!",
        "workflow_id": get_or_create_workflow_id
    }
    return await get_or_create_node_id(node_model=MessageNode, values=payload)


@pytest.fixture(scope="function")
async def get_or_create_condition_node_id(get_or_create_workflow_id: int) -> int:
    """
    Fixture for providing a ConditionNode object for the function scope.

    Returns:
        ConditionNode: Model instance.
    """
    payload = {
        "status_condition": Status.SENT,
        "workflow_id": get_or_create_workflow_id
    }
    return await get_or_create_node_id(node_model=ConditionNode, values=payload)


@pytest.fixture(scope="function")
async def get_or_create_end_node_id(get_or_create_workflow_id: int) -> int:
    """
    Fixture for providing a EndNode object for the function scope.

    Returns:
        EndNode: Model instance.
    """
    payload = {
        "workflow_id": get_or_create_workflow_id
    }
    return await get_or_create_node_id(node_model=EndNode, values=payload)
    