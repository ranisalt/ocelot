from typing import TextIO

import toml
from pydantic import BaseModel, Field

from .typing import Pvp


class Debug(BaseModel):
    enabled = False


class Database(BaseModel):
    host = "localhost"
    port = 3306
    username: str
    password: str
    name = Field("forgottenserver", alias="database")
    debug = False


class World(BaseModel):
    id: int
    name: str
    pvp: Pvp = Field(alias="pvp-type")
    address_protected: str = Field(alias="address-protected")
    port_protected: int = Field(alias="port-protected")
    address_unprotected: str = Field(alias="address-unprotected")
    port_unprotected: int = Field(alias="port-unprotected")


class Config(BaseModel):
    debug: Debug = Field(default_factory=Debug)
    database: Database | None
    worlds: dict[str, World]


def load_config(fp: str | TextIO) -> Config:
    parsed_toml = toml.load(fp)
    config = Config(**parsed_toml)

    assert len(config.worlds) == 1, "Only one world is supported."

    return config
