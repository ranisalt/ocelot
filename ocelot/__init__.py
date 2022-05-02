import os

import sqlalchemy
import sqlalchemy.orm
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from .config import Config, load_config
from .login.errors import (
    OcelotError,
    ocelot_exception_handler,
    request_validation_exception_handler,
)
from .login.routes import router as login_router

__version__ = "0.1.0"


def dsn_from_env(config: Config) -> str:
    # database_debug = os.environ.get("DATABASE_DEBUG")
    # echo = database_debug is not None and database_debug[0] in "1tTyY"

    if dsn := os.environ.get("DATABASE_URL"):
        return dsn

    if db := config.database:
        return (
            f"mysql+pymysql://{db.username}:{db.password}@{db.host}:{db.port}/{db.name}"
        )

    db_host = os.environ.get("MYSQL_HOST", "localhost")
    db_port = int(os.environ.get("MYSQL_PORT", "3306"))

    db_user = os.environ.get("MYSQL_USER")
    assert db_user is not None, "MYSQL_USER not set"
    assert db_user != "root", "MYSQL_USER must not be 'root'"

    db_pass = os.environ.get("MYSQL_PASSWORD")
    assert db_pass is not None, "MYSQL_PASSWORD not set"

    db_name = os.environ.get("MYSQL_DATABASE", "forgottenserver")
    return f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_exception_handler(OcelotError, ocelot_exception_handler)
    app.add_exception_handler(
        RequestValidationError, request_validation_exception_handler
    )
    app.include_router(login_router)

    @app.on_event("startup")
    async def startup():
        app.state.config = load_config("ocelot.toml")
        engine = sqlalchemy.create_engine(dsn_from_env(app.state.config))
        app.state.sessionmaker = sqlalchemy.orm.sessionmaker(bind=engine)

    return app


app = create_app()
