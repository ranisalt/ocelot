from typing import TextIO

import toml
from pydantic import BaseModel, Field

from .typing import Pvp


class World(BaseModel):
    id: int
    name: str
    pvp: Pvp = Field(alias="pvp-type")
    address_protected: str = Field(alias="address-protected")
    port_protected: int = Field(alias="port-protected")
    address_unprotected: str = Field(alias="address-unprotected")
    port_unprotected: int = Field(alias="port-unprotected")


class Config(BaseModel):
    worlds: dict[str, World]


def load_config(fp: TextIO) -> Config:
    parsed_toml = toml.load(fp)
    config = Config(**parsed_toml)

    assert len(config.worlds) == 1, "Only one world is supported."

    return config
