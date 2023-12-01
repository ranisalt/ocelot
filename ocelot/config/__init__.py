from typing import Literal, TextIO, Union

import toml
from pydantic import BaseModel, Field


class Debug(BaseModel):
    enabled: bool = False


class Database(BaseModel):
    host: str = "localhost"
    port: int = 3306
    username: str
    password: str
    name: str = Field("forgottenserver", alias="database")
    debug: bool = False


class _TokenSession(BaseModel):
    type: Literal["token"] = "token"


class _TFSSession(BaseModel):
    type: Literal["tfs"] = "tfs"


_Session = _TokenSession | _TFSSession


class Universe(BaseModel):
    name_generator: str | None = Field(alias="name-generator")
    minimum_password_length: int = Field(alias="minimum-password-generator", default=8)
    # private_key: str | None = Field(alias="private-key")
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

pvp_index_to_display_name: dict[int, str] = {
    0: "Open PvP",
    1: "Optional PvP",
    2: "Retro Hardcore PvP",
    # "Retro Open PvP"
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


class Config(BaseModel):
    debug: Debug = Field(default_factory=Debug)
    database: Database | None
    universe: Universe | None = Field(default_factory=Universe)
    worlds: dict[str, World] | None = Field(default_factory=dict)


def load_config(fp: str | TextIO) -> Config:
    parsed_toml = toml.load(fp)
    config = Config(**parsed_toml)

    assert len(config.worlds) == 1, "Only one world is supported."

    return config
