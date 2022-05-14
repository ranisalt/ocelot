import datetime
import hashlib
from dataclasses import asdict, dataclass

from ocelot.config import Config
from ocelot.config.typing import pvp_type_to_index
from ocelot.models import Account, OnlinePlayer, PlayerSex
from sqlalchemy import func
from sqlalchemy.orm import selectinload, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

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


@dataclass(slots=True)
class Session:
    sessionkey: str
    lastlogintime: int
    ispremium: bool
    premiumuntil: int
    status = "active"
    returnernotification = True
    showrewardnews = True
    isreturner = True
    fpstracking = True
    optiontracking = True
    tournamentticketpurchasestate = 0
    tournamentcyclephase = 0


@dataclass(slots=True)
class World:
    id: int
    name: str
    pvptype: int
    externaladdressprotected: str
    externalportprotected: int
    externaladdressunprotected: str
    externalportunprotected: int
    previewstate = 0
    location = "USA"
    anticheatprotection = False
    istournamentworld = False
    restrictedstore = False


@dataclass(slots=True)
class Character:
    worldid: int
    name: str
    level: int
    vocation: str
    ismale: bool
    outfitid: int
    headcolor: int
    torsocolor: int
    legscolor: int
    detailcolor: int
    addonsflags: int
    ishidden = False
    ismaincharacter = False
    tutorial = False
    istournamentparticipant = False
    dailyrewardstate = 0


@dataclass(slots=True)
class PlayData:
    worlds: list[World]
    characters: list[Character]


@dataclass(slots=True)
class LoginResponse:
    session: Session
    playdata: PlayData


async def login(request: Request):
    body = await request.json()

    match body["type"]:
        case "login":
            email, password = body.get("email"), body.get("password")
            if not email or not password:
                return error_response(ErrorCode.INVALID_CREDENTIALS)

            config: Config = request.app.state.config
            token = body.get("token", "")

            db: AsyncSession = request.app.state.sessionmaker
            async with db.begin():
                result = await db.execute(select(Account).options(selectinload(Account.characters)).where(Account.name == email))
                account = result.first()

            if not account:
                return error_response(ErrorCode.INVALID_CREDENTIALS)

            password_hash = hashlib.sha1(password.encode("ascii")).hexdigest()
            if account.password != password_hash:
                return error_response(ErrorCode.INVALID_CREDENTIALS)

            now = int(datetime.datetime.now().timestamp())

            session = Session(
                sessionkey=f"{email}\n{password}\n{token}\n{now}",
                lastlogintime=account.last_login,
                ispremium=account.premium_ends_at > now,
                premiumuntil=account.premium_ends_at,
            )

            world = next(world for world in config.worlds.values())

            worlds = [
                World(
                    id=world.id,
                    name=world.name,
                    pvptype=pvp_type_to_index[world.pvp],
                    externaladdressprotected=world.address_protected,
                    externalportprotected=world.port_protected,
                    externaladdressunprotected=world.address_unprotected,
                    externalportunprotected=world.port_unprotected,
                )
            ]

            characters = [
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
            ]

            resp = LoginResponse(
                session=session,
                playdata=PlayData(worlds=worlds, characters=characters),
            )
            return JSONResponse(asdict(resp))

        case _:  # pragma: no cover
            return error_response(ErrorCode.INTERNAL_ERROR)


@dataclass(slots=True)
class CacheInfoResponse:
    playersonline: int
    twitchstreams = 0
    twitchviewer = 0
    gamingyoutubestreams = 0
    gamingyoutubeviewer = 0


async def client(request: Request):
    body = await request.json()

    match body["type"]:
        # case "boostedcreature":
        #     ...

        case "cacheinfo":
            db: sessionmaker = request.app.state.sessionmaker
            async with db.begin():
                result = await db.execute(
                    select(OnlinePlayer).with_only_columns(func.count())
                )
                players_online: int = result.scalar_one()

            resp = CacheInfoResponse(playersonline=players_online)
            return JSONResponse(asdict(resp))

        # case "eventschedule":
        #     ...

        # case "news":
        #     ...

        case _:  # pragma: no cover
            return error_response(ErrorCode.INTERNAL_ERROR)


routes = [
    Route("/login", endpoint=login, methods=["POST"]),
    Route("/client", endpoint=client, methods=["POST"]),
]
