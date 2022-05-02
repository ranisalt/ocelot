import datetime
import hashlib
from typing import Literal

import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ocelot import config, models
from ocelot.config.api import get_config
from ocelot.config.typing import pvp_type_to_index
from ocelot.models.api import get_db

from .errors import ErrorCode, error_response

router = APIRouter()

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


class LoginRequest(BaseModel):
    type: Literal["login"]
    email: str
    password: str
    # optional in otclient, unused
    stayloggedin = False
    token = ""


class LoginResponse(BaseModel):
    class Session(BaseModel):
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

    class PlayData(BaseModel):
        class World(BaseModel):
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

        class Character(BaseModel):
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

        worlds: list[World]
        characters: list[Character]

    session: Session
    playdata: PlayData


@router.post("/login", response_model=LoginResponse)
async def login(
    req: LoginRequest,
    config: config.Config = Depends(get_config),
    db: sqlalchemy.orm.Session = Depends(get_db),
):
    match req.type:
        case "login":
            account = (
                db.query(models.Account).where(models.Account.name == req.email).first()
            )
            if not account:
                raise error_response(ErrorCode.INVALID_CREDENTIALS)

            password_hash = hashlib.sha1(req.password.encode("ascii")).hexdigest()
            if account.password != password_hash:
                raise error_response(ErrorCode.INVALID_CREDENTIALS)

            world = next(world for world in config.worlds.values())
            now = int(datetime.datetime.now().timestamp())

            return LoginResponse(
                session=LoginResponse.Session(
                    sessionkey=f"{req.email}\n{req.password}\n{req.token}\n{now}",
                    lastlogintime=account.last_login,
                    ispremium=account.premium_ends_at > now,
                    premiumuntil=account.premium_ends_at,
                ),
                playdata=LoginResponse.PlayData(
                    worlds=[
                        LoginResponse.PlayData.World(
                            id=world.id,
                            name=world.name,
                            pvptype=pvp_type_to_index[world.pvp],
                            externaladdressprotected=world.address_protected,
                            externalportprotected=world.port_protected,
                            externaladdressunprotected=world.address_unprotected,
                            externalportunprotected=world.port_unprotected,
                        )
                    ],
                    characters=[
                        LoginResponse.PlayData.Character(
                            worldid=world.id,
                            name=character.name,
                            level=character.level,
                            vocation=vocation_index_to_name[character.vocation],
                            ismale=character.sex == models.PlayerSex.Male,
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

        case _:  # pragma: no cover
            raise error_response(ErrorCode.INTERNAL_ERROR)


class BoostedCreatureRequest(BaseModel):
    type: Literal["boostedcreature"]


class CacheInfoRequest(BaseModel):
    type: Literal["cacheinfo"]


class CacheInfoResponse(BaseModel):
    playersonline: int
    twitchstreams = 0
    twitchviewer = 0
    gamingyoutubestreams = 0
    gamingyoutubeviewer = 0


class EventScheduleRequest(BaseModel):
    type: Literal["eventschedule"]


class NewsRequest(BaseModel):
    type: Literal["news"]
    count: int = Field(alias="count")
    is_returner: bool = Field(alias="isreturner")
    offset: int = Field(alias="offset")
    show_reward_news: bool = Field(alias="showrewardnews")


@router.post("/client", response_model=CacheInfoResponse)
async def client(
    req: BoostedCreatureRequest | CacheInfoRequest | EventScheduleRequest | NewsRequest,
    db: sqlalchemy.orm.Session = Depends(get_db),
):
    match req.type:
        # case "boostedcreature":
        #     ...

        case "cacheinfo":
            return CacheInfoResponse(
                playersonline=db.query(models.OnlinePlayer).count()
            )

        # case "eventschedule":
        #     ...

        # case "news":
        #     ...

        case _:  # pragma: no cover
            raise error_response(ErrorCode.INTERNAL_ERROR)


@router.post("/")
async def catch_all(path):
    # print(f"{request.method} /{path} {request.json}")
    raise error_response(ErrorCode.INTERNAL_ERROR)
