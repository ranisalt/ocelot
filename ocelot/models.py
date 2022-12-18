import enum
import os

from tortoise import fields, models

from ocelot.config import Config


class PlayerSex(enum.IntEnum):
    Female = 0
    Male = 1


class Account(models.Model):
    class Meta:
        table = "accounts"

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32, unique=True)
    password = fields.CharField(max_length=40)
    secret = fields.CharField(max_length=16, null=True)
    premium_ends_at = fields.IntField(default=0)
    email = fields.CharField(max_length=254, default="")

    characters: fields.ReverseRelation["Character"]


class Character(models.Model):
    class Meta:
        table = "players"

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    level = fields.IntField(default=1)
    account: fields.ForeignKeyRelation[Account] = fields.ForeignKeyField(
        "models.Account", related_name="characters"
    )
    vocation = fields.IntField(default=0)
    look_type = fields.IntField(source_field="looktype", default=136)
    look_head = fields.IntField(source_field="lookhead", default=0)
    look_body = fields.IntField(source_field="lookbody", default=0)
    look_legs = fields.IntField(source_field="looklegs", default=0)
    look_feet = fields.IntField(source_field="lookfeet", default=0)
    look_addons = fields.IntField(source_field="lookaddons", default=0)
    sex = fields.IntEnumField(PlayerSex)
    last_login_at = fields.IntField(source_field="lastlogin", default=0)


class OnlinePlayer(models.Model):
    class Meta:
        table = "players_online"

    player_id = fields.IntField(pk=True)


def database_from_env(config: Config) -> str:
    if dsn := os.environ.get("DATABASE_URL"):
        return dsn

    if db := config.database:
        return f"mysql://{db.username}:{db.password}@{db.host}:{db.port}/{db.name}"

    db_host = os.environ.get("MYSQL_HOST", "localhost")
    db_port = int(os.environ.get("MYSQL_PORT", "3306"))

    db_user = os.environ.get("MYSQL_USER")
    assert db_user is not None, "MYSQL_USER not set"
    assert db_user != "root", "MYSQL_USER must not be 'root'"

    db_pass = os.environ.get("MYSQL_PASSWORD")
    assert db_pass is not None, "MYSQL_PASSWORD not set"

    db_name = os.environ.get("MYSQL_DATABASE", "forgottenserver")
    return f"mysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
