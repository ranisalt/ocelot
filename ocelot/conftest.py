import io

import pytest

from .config import Config, load_config


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def config() -> Config:
    fp = io.StringIO(
        """
        [debug]
        enabled = true

        [database]
        database = "test"
        username = "test"
        password = "test"

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
