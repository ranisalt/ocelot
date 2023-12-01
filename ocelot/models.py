import enum

from tortoise import fields, models
from .fields import BinaryField


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
    last_ip = BinaryField(source_field="lastip", max_length=16, default="")


class OnlinePlayer(models.Model):
    class Meta:
        table = "players_online"

    player_id = fields.IntField(pk=True)
