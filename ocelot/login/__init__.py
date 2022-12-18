from starlette.applications import Starlette
from tortoise.contrib.starlette import register_tortoise

from ocelot.config import Config
from ocelot.session import SessionManager

from .routes import routes as login_routes


def create_app(config: Config, session_manager: SessionManager, **kwargs) -> Starlette:
    app = Starlette(debug=config.debug.enabled, routes=login_routes)
    app.state.config = config
    app.state.session_manager = session_manager
    register_tortoise(app, modules={"models": ["ocelot.models"]}, **kwargs)

    return app
