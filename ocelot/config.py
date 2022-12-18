from typing import Literal, TextIO, Union

import toml
from pydantic import BaseModel, Field


class Debug(BaseModel):
    enabled = False


class Database(BaseModel):
    host = "localhost"
    port = 3306
    username: str
    password: str
    name = Field("forgottenserver", alias="database")
    debug = False


class _TokenSession(BaseModel):
    type: Literal["token"] = "token"


class _TFSSession(BaseModel):
    type: Literal["tfs"] = "tfs"


_Session = _TokenSession | _TFSSession


class Universe(BaseModel):
    private_key: str | None = Field(alias="private-key")
    session: _Session = Field(alias="session", default_factory=_TokenSession)


OptionalPvp = Union[Literal["no-pvp"], Literal["optional"]]
OpenPvp = Union[Literal["pvp"], Literal["open"]]
HardcorePvp = Union[Literal["pvp-enforced"], Literal["hardcore"]]
Pvp = Union[OptionalPvp, OpenPvp, HardcorePvp]

pvp_type_to_index: dict[str, int] = {
    "pvp": 0,
    "open": 0,
    "no-pvp": 1,
    "optional": 1,
    "pvp-enforced": 2,
    "hardcore": 2,
}


class Map(BaseModel):
    type: Literal["otbm"] = "otbm"
    file: str


class World(BaseModel):
    id: int
    name: str
    pvp: Pvp = Field(alias="pvp-type")
    address_protected: str = Field(alias="address-protected")
    port_protected: int = Field(alias="port-protected")
    address_unprotected: str = Field(alias="address-unprotected")
    port_unprotected: int = Field(alias="port-unprotected")
    map: Map


class Config(BaseModel):
    debug: Debug = Field(default_factory=Debug)
    database: Database | None
    universe: Universe = Field(default_factory=Universe)
    worlds: dict[str, World]


def load_config(fp: str | TextIO) -> Config:
    parsed_toml = toml.load(fp)
    config = Config(**parsed_toml)

    assert len(config.worlds) == 1, "Only one world is supported."

    return config


__all__ = ["Config", "Pvp", "load_config"]
