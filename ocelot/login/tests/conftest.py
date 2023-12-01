import datetime

import pytest
from starlette.testclient import TestClient

from ocelot.config import Config

from .. import create_app

fake_now = datetime.datetime(2020, 12, 25, 17, 5, 55)


@pytest.fixture
def client(config: Config):
    app = create_app(config, db_url="sqlite://:memory:", generate_schemas=True)

    with TestClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def mocked_now(monkeypatch: pytest.MonkeyPatch) -> datetime.datetime:
    class _datetime:
        @classmethod
        def now(cls):
            return fake_now

    monkeypatch.setattr(datetime, "datetime", _datetime)
    return fake_now
