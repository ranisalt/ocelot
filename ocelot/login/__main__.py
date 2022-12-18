import argparse
from os import getcwd, path

import uvicorn

from ocelot.config import load_config
from ocelot.models import database_from_env
from ocelot.session import session_from_config

from . import create_app

parser = argparse.ArgumentParser()
parser.add_argument("--config", "-c", type=str, default="./ocelot.toml")
parser.add_argument("--debug", "-d", action="store_true", default=False)
args = parser.parse_args()

with open(path.join(getcwd(), args.config)) as fp:
    config = load_config(fp)

db_url = database_from_env(config)
session_manager = session_from_config(config.universe.session)
app = create_app(config=config, db_url=db_url, session_manager=session_manager)

uvicorn.run(app, debug=args.debug)
