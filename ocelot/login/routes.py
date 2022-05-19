import datetime
import enum
import hashlib

from databases import Database
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from ocelot.config import Config
from ocelot.config.typing import pvp_type_to_index

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


class PlayerSex(enum.IntEnum):
    Female = 0
    Male = 1


async def login(request: Request):
    body = await request.json()

    match body["type"]:
        case "login":
            email, password = body.get("email"), body.get("password")
            if not email or not password:
                return error_response(ErrorCode.INVALID_CREDENTIALS)

            db: Database = request.app.state.database
            account = await db.fetch_one(
                query="SELECT id, password, premium_ends_at FROM accounts WHERE name = :name",
                values={"name": email},
            )

            if not account:
                return error_response(ErrorCode.INVALID_CREDENTIALS)

            password_hash = hashlib.sha1(password.encode("ascii")).hexdigest()
            if account["password"] != password_hash:
                return error_response(ErrorCode.INVALID_CREDENTIALS)

            now = int(datetime.datetime.now().timestamp())

            account_characters = await db.fetch_all(
                query="SELECT name, level, vocation, looktype, lookhead, lookbody, looklegs, lookfeet, lookaddons, sex, lastlogin FROM players WHERE account_id = :account_id",
                values={"account_id": account["id"]},
            )

            token = body.get("token", "")
            session = {
                "sessionkey": f"{email}\n{password}\n{token}\n{now}",
                "lastlogintime": max(c["lastlogin"] for c in account_characters),
                "ispremium": account["premium_ends_at"] > now,
                "premiumuntil": account["premium_ends_at"],
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
                        "name": character["name"],
                        "level": character["level"],
                        "vocation": vocation_index_to_name[character["vocation"]],
                        "ismale": character["sex"] == PlayerSex.Male,
                        "outfitid": character["looktype"],
                        "headcolor": character["lookhead"],
                        "torsocolor": character["lookbody"],
                        "legscolor": character["looklegs"],
                        "detailcolor": character["lookfeet"],
                        "addonsflags": character["lookaddons"],
                        # not implemented
                        "ishidden": False,
                        "ismaincharacter": False,
                        "tutorial": False,
                        "istournamentparticipant": False,
                        "dailyrewardstate": 0,
                    }
                    for character in account_characters
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
            db: Database = request.app.state.database

            players_online: int = await db.fetch_val(
                query="SELECT COUNT(*) FROM players_online"
            )

            return JSONResponse({"playersonline": players_online})

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
