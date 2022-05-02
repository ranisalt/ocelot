import enum

import sqlalchemy
import sqlalchemy.orm

mapper_registry: sqlalchemy.orm.registry = sqlalchemy.orm.registry()


class PlayerSex(enum.IntEnum):
    Female = 0
    Male = 1


@mapper_registry.mapped
class Account:
    __tablename__ = "accounts"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(32), unique=True)
    password = sqlalchemy.Column(sqlalchemy.String(40))
    # secret = Optional(str)
    premium_ends_at = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    # email = sqlalchemy.Column(sqlalchemy.String)

    characters: list["Character"] = sqlalchemy.orm.relationship("Character")

    @property
    def last_login(self) -> int:
        return max(c.last_login or 0 for c in self.characters)


@mapper_registry.mapped
class Character:
    __tablename__ = "players"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), unique=True)
    level = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    account_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("accounts.id"), nullable=False
    )
    vocation = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    look_type = sqlalchemy.Column("looktype", sqlalchemy.Integer, default=136)
    look_head = sqlalchemy.Column("lookhead", sqlalchemy.Integer, default=0)
    look_body = sqlalchemy.Column("lookbody", sqlalchemy.Integer, default=0)
    look_legs = sqlalchemy.Column("looklegs", sqlalchemy.Integer, default=0)
    look_feet = sqlalchemy.Column("lookfeet", sqlalchemy.Integer, default=0)
    look_addons = sqlalchemy.Column("lookaddons", sqlalchemy.Integer, default=0)
    sex = sqlalchemy.Column(sqlalchemy.Integer)
    last_login = sqlalchemy.Column("lastlogin", sqlalchemy.Integer, default=0)

    # account: Account = sqlalchemy.orm.relationship("Account", back_populates="characters")


@mapper_registry.mapped
class OnlinePlayer:
    __tablename__ = "players_online"

    player_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
