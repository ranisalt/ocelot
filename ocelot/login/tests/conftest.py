import datetime

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from ocelot import create_app
from ocelot.config import Config

fake_now = datetime.datetime(2020, 12, 25, 17, 5, 55)


@pytest.fixture
async def client(config: Config):
    app = create_app(config, db_url="sqlite://:memory:", generate_schemas=True)

    async with LifespanManager(app):
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
