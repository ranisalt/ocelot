import datetime
import io

import pytest
from flask import Flask
from flask.testing import FlaskClient
from pony.orm import Database

from ..config import Config, load_config

fake_now = datetime.datetime(2020, 12, 25, 17, 5, 55)


@pytest.fixture()
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


@pytest.fixture(scope="session")
def bound_db() -> Database:
    from ..database import db

    db.bind({"provider": "sqlite", "filename": ":memory:"})
    db.generate_mapping(create_tables=True)
    return db


@pytest.fixture()
def app(config: Config, bound_db: Database):
    from .. import create_app

    app = create_app()
    app.config.update(
        {
            "OCELOT": config,
            "TESTING": True,
        }
    )

    bound_db.create_tables()
    yield app
    bound_db.drop_all_tables(with_all_data=True)


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def mocked_now(monkeypatch: pytest.MonkeyPatch) -> datetime.datetime:
    class _datetime:
        @classmethod
        def now(cls):
            return fake_now

    monkeypatch.setattr(datetime, "datetime", _datetime)
    return fake_now
