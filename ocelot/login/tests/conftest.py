import datetime
from typing import Generator

import pytest
import sqlalchemy
import sqlalchemy.orm
from fastapi.testclient import TestClient

from ... import create_app
from ...config import Config
from ..routes import get_config, get_db

fake_now = datetime.datetime(2020, 12, 25, 17, 5, 55)


@pytest.fixture()
def client(config: Config, db_session: sqlalchemy.orm.sessionmaker):
    def _get_config() -> Config:
        return config

    def _get_db() -> Generator[sqlalchemy.orm.Session, None, None]:
        with db_session() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_config] = _get_config
    app.dependency_overrides[get_db] = _get_db
    return TestClient(app)


@pytest.fixture()
def mocked_now(monkeypatch: pytest.MonkeyPatch) -> datetime.datetime:
    class _datetime:
        @classmethod
        def now(cls):
            return fake_now

    monkeypatch.setattr(datetime, "datetime", _datetime)
    return fake_now
