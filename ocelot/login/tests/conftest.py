import datetime

import pytest
from databases import Database
from httpx import AsyncClient

from ... import create_app
from ...config import Config

fake_now = datetime.datetime(2020, 12, 25, 17, 5, 55)


@pytest.fixture
async def database(config: Config):
    assert config.database
    database = Database(
        f"mysql://{config.database.username}:{config.database.password}@{config.database.host}:{config.database.port}/{config.database.name}",
        force_rollback=True,
    )

    await database.connect()
    yield database
    await database.disconnect()


@pytest.fixture
async def client(config: Config, database: Database):
    app = create_app(config, database)

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def mocked_now(monkeypatch: pytest.MonkeyPatch) -> datetime.datetime:
    class _datetime:
        @classmethod
        def now(cls):
            return fake_now

    monkeypatch.setattr(datetime, "datetime", _datetime)
    return fake_now
