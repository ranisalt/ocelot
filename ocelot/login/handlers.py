import datetime
import hashlib

from ocelot.login.enums import PlayerSex

from . import config as c
from .database import Account
from .errors import InvalidCredentials
from .models import Character, LoginResponse, PlayData, Session, World

pvp_type_to_index: dict[str, int] = {
    "pvp": 0,
    "open": 0,
    "no-pvp": 1,
    "optional": 1,
    "pvp-enforced": 2,
    "hardcore": 2,
}

vocation_index_to_name: dict[int, str] = {
    0: "None",
    1: "Sorcerer",
    2: "Druid",
    3: "Paladin",
    4: "Knight",
    5: "Master Sorcerer",
    6: "Elder Druid",
    7: "Royal Paladin",
    8: "Elite Knight",
}


def login(
    config: c.Config, email: str, password: str, token: str | None = None
) -> LoginResponse:
    account: Account = Account.get(name=email)
    if not account:
        raise InvalidCredentials

    password_hash = hashlib.sha1(password.encode("ascii")).hexdigest()
    if account.password != password_hash:
        raise InvalidCredentials

    world = next(world for world in config.worlds.values())
    now = int(datetime.datetime.now().timestamp())

    return LoginResponse(
        session=Session(
            sessionkey=f"{email}\n{password}\n{token}\n{now}",
            lastlogintime=account.last_login,
            ispremium=account.premium_ends_at > now,
            premiumuntil=account.premium_ends_at,
        ),
        playdata=PlayData(
            worlds=[
                World(
                    id=world.id,
                    name=world.name,
                    pvptype=pvp_type_to_index[world.pvp],
                    addressprotected=world.address_protected,
                    portprotected=world.port_protected,
                    addressunprotected=world.address_unprotected,
                    portunprotected=world.port_unprotected,
                )
            ],
            characters=[
                Character(
                    worldid=world.id,
                    name=character.name,
                    level=character.level,
                    vocation=vocation_index_to_name[character.vocation],
                    ismale=character.sex == PlayerSex.Male,
                    outfitid=character.look_type,
                    headcolor=character.look_head,
                    torsocolor=character.look_body,
                    legscolor=character.look_legs,
                    detailcolor=character.look_feet,
                    addonsflags=character.look_addons,
                )
                for character in account.characters
            ],
        ),
    )
