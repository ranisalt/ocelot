import datetime
import hashlib
from typing import Optional

from flask import Blueprint, current_app, request
from pony import orm

from .config import Config, World
from .database import Account, OnlinePlayer
from .enums import PlayerSex
from .errors import ErrorCode, error_response
from .typing import Pvp

router = Blueprint("login", __name__)

session_defaults = {
    "status": "active",
    "returnernotification": False,
    "showrewardnews": False,
    "isreturner": False,
    "fpstracking": False,
    "optiontracking": False,
    "tournamentticketpurchasestate": 0,
    "tournamentcyclephase": 0,
}

world_defaults = {
    "previewstate": 0,
    "location": "USA",
    "anticheatprotection": False,
    "istournamentworld": False,
    "restrictedstore": False,
}

player_defaults = {
    "ishidden": False,
    "ismaincharacter": False,
    "tutorial": False,
    "istournamentparticipant": False,
    "dailyrewardstate": 0,
}

cacheinfo_defaults = {
    "twitchstreams": 0,
    "twitchviewer": 0,
    "gamingyoutubestreams": 0,
    "gamingyoutubeviewer": 0,
}

pvp_type_to_index: dict[Pvp, int] = {
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


def get_world() -> World:
    config: Config = current_app.config["OCELOT"]
    return next(world for world in config.worlds.values())


@router.post("/login")
@router.post("/login.php")
def login():
    match type_ := request.json["type"]:
        case "login":
            email: Optional[str] = request.json.get("email")
            password: Optional[str] = request.json.get("password")

            if not email or not password:
                return error_response(ErrorCode.INVALID_CREDENTIALS)

            account: Account = Account.get(name=email)
            if not account:
                return error_response(ErrorCode.INVALID_CREDENTIALS)

            password_hash = hashlib.sha1(password.encode("ascii")).hexdigest()
            if account.password != password_hash:
                return error_response(ErrorCode.INVALID_CREDENTIALS)

            # optional in otclient
            # stay_logged_in: bool = request.json.get("stayloggedin", False)
            token: str = request.json.get("token", "")
            now = int(datetime.datetime.now().timestamp())

            world = get_world()

            return {
                "session": {
                    "sessionkey": f"{email}\n{password}\n{token}\n{now}",
                    "lastlogintime": account.last_login,
                    "ispremium": account.premium_ends_at > now,
                    "premiumuntil": account.premium_ends_at,
                    **session_defaults,
                },
                "playdata": {
                    "worlds": [
                        {
                            "id": world.id,
                            "name": world.name,
                            "pvp-type": pvp_type_to_index[world.pvp],
                            "address-protected": world.address_protected,
                            "port-protected": world.port_protected,
                            "address-unprotected": world.address_unprotected,
                            "port-unprotected": world.port_unprotected,
                            **world_defaults,
                        }
                    ],
                    "characters": [
                        {
                            "worldid": world.id,
                            "name": character.name,
                            "level": character.level,
                            "vocation": vocation_index_to_name[character.vocation],
                            "ismale": character.sex == PlayerSex.Male,
                            "outfitid": character.look_type,
                            "headcolor": character.look_head,
                            "torsocolor": character.look_body,
                            "legscolor": character.look_legs,
                            "detailcolor": character.look_feet,
                            "addonsflags": character.look_addons,
                        }
                        for character in account.characters
                    ],
                },
            }

        case _:  # pragma: no cover
            return error_response(ErrorCode.INTERNAL_ERROR)


@router.post("/client")
@router.post("/client.php")
def client():
    match type_ := request.json["type"]:
        # case "boostedcreature":
        #     ...

        case "cacheinfo":
            return {
                "playersonline": orm.count(_ for _ in OnlinePlayer),
                **cacheinfo_defaults,
            }

        # case "eventschedule":
        #     ...

        # case "news":
        #     count: int = request.json["count"]
        #     is_returner: bool = request.json["isreturner"]
        #     offset: int = request.json["offset"]
        #     show_reward_news: bool = request.json["showrewardnews"]
        #     ...

        case _:  # pragma: no cover
            return error_response(ErrorCode.INTERNAL_ERROR)


# @router.post("/", defaults={"path": ""})
# @router.post("/<path:path>")
# def catch_all(path):
#     print(f"{request.method} /{path} {request.json}")
