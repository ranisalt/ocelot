import io

import pytest
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from ocelot.config import Config, load_config
from ocelot.models import mapper_registry


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def config() -> Config:
    fp = io.StringIO(
        """
        [worlds.default]
        id = 0
        name = "Antica"
        pvp-type = "pvp"
        address-protected = "prod-cf-eu.tibia.com"
        port-protected = 7171
        address-unprotected = "prod-lb-eu.tibia.com"
        port-unprotected = 7171
        """
    )
    return load_config(fp)


@pytest.fixture
async def db_session():
    async_engine = create_async_engine(
        "sqlite+aiosqlite://",
        future=True,
        connect_args={"check_same_thread": False},
    )
    # async_engine = create_async_engine(
    #     "mysql+asyncmy://test:test@localhost:3306/test", future=True
    # )

    async with async_engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.create_all)

    async_session = sqlalchemy.orm.sessionmaker(
        bind=async_engine, future=True, expire_on_commit=False, class_=AsyncSession
    )
    yield async_session()

    async with async_engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.drop_all)

    await async_engine.dispose()
