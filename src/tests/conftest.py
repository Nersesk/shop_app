import asyncio
import os

import pytest
import pytest_asyncio
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.configs import tmp_settings
from src.products.models import Base
from ..main import app
from ..session_create import get_async_session

engine_test = create_async_engine(tmp_settings.DATABASE_URL_asyncpg, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine_test, expire_on_commit=False)
Base.metadata.bind = engine_test


@pytest_asyncio.fixture
async def session():
    async with async_session_maker() as session:
        yield session

# Override FastAPI dependency before tests run
@pytest_asyncio.fixture(autouse=True, scope="session")
def override_get_async_session():
    async def _override():
        async with async_session_maker() as session:
            yield session
    app.dependency_overrides[get_async_session] = _override
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


