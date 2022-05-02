import io

import pytest
import sqlalchemy
import sqlalchemy.orm

from ocelot.config import Config, load_config
from ocelot.models import mapper_registry


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


@pytest.fixture()
def db_session():
    # engine = sqlalchemy.create_engine(
    #     "sqlite://", connect_args={"check_same_thread": False}
    # )
    engine = sqlalchemy.create_engine(
        "mysql+pymysql://forgottenserver:forgottenserver@localhost:3306/forgottenserver"
    )
    mapper_registry.metadata.create_all(bind=engine)

    yield sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
    mapper_registry.metadata.drop_all(bind=engine)
