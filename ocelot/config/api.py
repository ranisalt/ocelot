from functools import cache

from . import load_config


@cache
def get_config():
    with open("ocelot.toml") as fp:
        return load_config(fp)
