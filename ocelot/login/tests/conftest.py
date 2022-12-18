import datetime
import secrets
from typing import Callable

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from ocelot.config import Config
from ocelot.session import session_from_config

from .. import create_app

fake_now = datetime.datetime(2020, 12, 25, 17, 5, 55)


@pytest.fixture
async def client(config: Config):
    session_manager = session_from_config(config.universe.session)
    app = create_app(
        config,
        db_url="sqlite://:memory:",
        session_manager=session_manager,
        generate_schemas=True,
    )

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


@pytest.fixture(autouse=True)
def mocked_token_bytes(monkeypatch: pytest.MonkeyPatch) -> Callable[[int], bytes]:
    def _token_bytes(length: int) -> bytes:
        return b"\x00" * length

    monkeypatch.setattr(secrets, "token_bytes", _token_bytes)
    return _token_bytes
