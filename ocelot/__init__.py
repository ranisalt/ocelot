import os

from databases import Database
from starlette.applications import Starlette

from .config import Config, load_config
from .login.routes import routes as login_routes

__version__ = "0.1.0"


def database_from_env(config: Config) -> Database:
    # database_debug = os.environ.get("DATABASE_DEBUG")
    # echo = database_debug is not None and database_debug[0] in "1tTyY"

    if dsn := os.environ.get("DATABASE_URL"):
        return Database(dsn)

    if db := config.database:
        return Database(
            f"mysql://{db.username}:{db.password}@{db.host}:{db.port}/{db.name}"
        )

    db_host = os.environ.get("MYSQL_HOST", "localhost")
    db_port = int(os.environ.get("MYSQL_PORT", "3306"))

    db_user = os.environ.get("MYSQL_USER")
    assert db_user is not None, "MYSQL_USER not set"
    assert db_user != "root", "MYSQL_USER must not be 'root'"

    db_pass = os.environ.get("MYSQL_PASSWORD")
    assert db_pass is not None, "MYSQL_PASSWORD not set"

    db_name = os.environ.get("MYSQL_DATABASE", "forgottenserver")
    return Database(f"mysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")


def create_app(config: Config, database: Database) -> Starlette:
    app = Starlette(debug=config.debug.enabled, routes=login_routes)
    app.state.config = config
    app.state.database = database

    return app


def default_app():
    with open("ocelot.toml") as fp:
        config = load_config(fp)

    database = database_from_env(config)
    app = create_app(config, database)

    @app.on_event("startup")
    async def startup():
        await app.state.database.connect()

    @app.on_event("shutdown")
    async def shutdown():
        await app.state.database.disconnect()

    return app
