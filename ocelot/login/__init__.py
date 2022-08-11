from starlette.applications import Starlette
from tortoise.contrib.starlette import register_tortoise

from ocelot import database_from_env
from ocelot.config import Config, load_config

from .routes import routes as login_routes


def create_app(config: Config, **kwargs) -> Starlette:
    app = Starlette(debug=config.debug.enabled, routes=login_routes)
    app.state.config = config
    register_tortoise(app, modules={"models": ["ocelot.models"]}, **kwargs)

    return app


def default_app():
    with open("ocelot.toml") as fp:
        config = load_config(fp)

    db_url = database_from_env(config)
    app = create_app(config, db_url=f"{db_url}?maxsize=10")

    return app
