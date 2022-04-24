from flask import Flask, current_app
from pony.flask import Pony

from .config import load_config
from .database import db, db_config_from_env
from .routes import router


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(router)
    Pony(app)
    return app


def bind_database():
    if not app.config.get("OCELOT"):
        with open("ocelot.toml") as fp:
            app.config["OCELOT"] = load_config(fp)

    if not app.config.get("PONY"):
        app.config["PONY"] = db_config_from_env()

    pony_config = current_app.config["PONY"]
    db.bind(**pony_config)
    db.generate_mapping(create_tables=False)


app = create_app()
app.before_first_request(bind_database)
