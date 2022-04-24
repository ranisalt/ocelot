# We need this to avoid `TypeError: 'type' object is not subscriptable`
# later on when forward declaring relation types with strings
from __future__ import annotations

import os

from pony.orm import Database, PrimaryKey, Required, Set

from .enums import PlayerSex

db = Database()

# Using `db.Entity` directly won't work, as both MyPy and Pyright won't
# allow inheriting a class from a variable. For Pyright this declaration
# is enough misdirection for it not to complain, but MyPy needs an extra
# `type: ignore` comment above each model declaration to work.


class Account(db.Entity):  # type: ignore
    _table_ = "accounts"

    id = PrimaryKey(int, auto=True)
    name = Required(str, max_len=32, unique=True)
    password = Required(str)
    # secret = Optional(str)
    premium_ends_at = Required(int, column="premium_ends_at", default=0)
    # email = Required(str)

    characters: Set["Character"] = Set("Character")

    @property
    def last_login(self) -> int:
        return max((c.last_login for c in self.characters), default=0)


class Character(db.Entity):  # type: ignore
    _table_ = "players"

    id = PrimaryKey(int, auto=True)
    name = Required(str, max_len=255, unique=True)
    account = Required(Account, column="account_id", fk_name="account_id")
    level = Required(int, default=1)
    vocation = Required(int, default=0)
    look_type = Required(int, column="looktype", default=136)
    look_head = Required(int, column="lookhead", default=0)
    look_body = Required(int, column="lookbody", default=0)
    look_legs = Required(int, column="looklegs", default=0)
    look_feet = Required(int, column="lookfeet", default=0)
    look_addons = Required(int, column="lookaddons", default=0)
    sex = Required(PlayerSex)
    last_login = Required(int, column="lastlogin", default=0)


class OnlinePlayer(db.Entity):  # type: ignore
    _table_ = "players_online"

    player_id = PrimaryKey(int)


def db_config_from_env() -> dict:
    db_host = os.environ.get("MYSQL_HOST", "localhost")
    db_port = int(os.environ.get("MYSQL_PORT", "3306"))

    db_user = os.environ.get("MYSQL_USER")
    assert db_user is not None, "MYSQL_USER not set"
    assert db_user != "root", "MYSQL_USER must not be 'root'"

    db_pass = os.environ.get("MYSQL_PASSWORD")
    assert db_pass is not None, "MYSQL_PASSWORD not set"

    db_name = os.environ.get("MYSQL_DATABASE", "forgottenserver")
    return {
        "provider": "mysql",
        "host": db_host,
        "port": db_port,
        "user": db_user,
        "passwd": db_pass,
        "db": db_name,
    }
