import datetime
import hashlib

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from ocelot.config import Config
from ocelot.config.typing import pvp_type_to_index
from ocelot.models import Account, OnlinePlayer, PlayerSex

from .errors import ErrorCode, error_response

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


async def login(request: Request):
    body = await request.json()

    match body["type"]:
        case "login":
            email, password = body.get("email"), body.get("password")
            if not email or not password:
                return error_response(ErrorCode.INVALID_CREDENTIALS)

            account = await Account.get_or_none(name=email)
            if not account:
                return error_response(ErrorCode.INVALID_CREDENTIALS)

            password_hash = hashlib.sha1(password.encode("ascii")).hexdigest()
            if account.password != password_hash:
                return error_response(ErrorCode.INVALID_CREDENTIALS)

            now = int(datetime.datetime.now().timestamp())
            token = body.get("token", "")

            last_login_time = max([c.last_login_at async for c in account.characters])
            session = {
                "sessionkey": f"{email}\n{password}\n{token}\n{now}",
                "lastlogintime": last_login_time,
                "ispremium": account.premium_ends_at > now,
                "premiumuntil": account.premium_ends_at,
                # not implemented
                "status": "active",
                "returnernotification": True,
                "showrewardnews": True,
                "isreturner": True,
                "fpstracking": True,
                "optiontracking": True,
                "tournamentticketpurchasestate": 0,
                "tournamentcyclephase": 0,
            }

            config: Config = request.app.state.config
            world = next(world for world in config.worlds.values())

            playdata = {
                "worlds": [
                    {
                        "id": world.id,
                        "name": world.name,
                        "pvptype": pvp_type_to_index[world.pvp],
                        "externaladdressprotected": world.address_protected,
                        "externalportprotected": world.port_protected,
                        "externaladdressunprotected": world.address_unprotected,
                        "externalportunprotected": world.port_unprotected,
                        # not implemented
                        "previewstate": 0,
                        "location": "USA",
                        "anticheatprotection": False,
                        "istournamentworld": False,
                        "restrictedstore": False,
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
                        # not implemented
                        "ishidden": False,
                        "ismaincharacter": False,
                        "tutorial": False,
                        "istournamentparticipant": False,
                        "dailyrewardstate": 0,
                    }
                    async for character in account.characters
                ],
            }

            return JSONResponse({"session": session, "playdata": playdata})

        case _:  # pragma: no cover
            return error_response(ErrorCode.INTERNAL_ERROR)


async def client(request: Request):
    body = await request.json()

    match body["type"]:
        # case "boostedcreature":
        #     ...

        case "cacheinfo":
            return JSONResponse({"playersonline": await OnlinePlayer.all().count()})

        # case "eventschedule":
        #     ...

        # case "news":
        #     ...

        case _:  # pragma: no cover
            return error_response(ErrorCode.INTERNAL_ERROR)


routes = [
    Route("/login", login, methods=["POST"]),
    Route("/client", client, methods=["POST"]),
]
