import os

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from starlette.applications import Starlette

from .config import Config, load_config
from .login.routes import routes as login_routes

__version__ = "0.1.0"


def dsn_from_env(config: Config) -> str:
    # database_debug = os.environ.get("DATABASE_DEBUG")
    # echo = database_debug is not None and database_debug[0] in "1tTyY"

    if dsn := os.environ.get("DATABASE_URL"):
        return dsn

    if db := config.database:
        return (
            f"mysql+asyncmy://{db.username}:{db.password}@{db.host}:{db.port}/{db.name}"
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


def create_app() -> Starlette:
    app = Starlette(routes=login_routes)

    @app.on_event("startup")
    async def startup():
        config = load_config("ocelot.toml")
        app.state.config = config

        engine = create_async_engine(
            dsn_from_env(app.state.config), echo=config.database.debug, future=True
        )
        app.state.sessionmaker = sqlalchemy.orm.sessionmaker(
            bind=engine, future=True, class_=AsyncSession
        )

    return app


app = create_app()
