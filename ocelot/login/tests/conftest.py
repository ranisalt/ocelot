import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.testclient import TestClient

from ... import create_app
from ...config import Config

fake_now = datetime.datetime(2020, 12, 25, 17, 5, 55)


@pytest.fixture
def client(config: Config, db_session: AsyncSession):
    app = create_app()
    app.state.config = config
    app.state.sessionmaker = db_session
    return TestClient(app)


@pytest.fixture
def mocked_now(monkeypatch: pytest.MonkeyPatch) -> datetime.datetime:
    class _datetime:
        @classmethod
        def now(cls):
            return fake_now

    monkeypatch.setattr(datetime, "datetime", _datetime)
    return fake_now
