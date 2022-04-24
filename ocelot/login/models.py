from typing import Literal

from pydantic import BaseModel


class Session(BaseModel):
    sessionkey: str
    lastlogintime: int
    ispremium: bool
    premiumuntil: int
    status: Literal["active"] = "active"
    returnernotification = False
    showrewardnews = False
    isreturner = False
    fpstracking = False
    optiontracking = False
    tournamentticketpurchasestate = 0
    tournamentcyclephase = 0


class World(BaseModel):
    id: int
    name: str
    pvptype: int
    addressprotected: str
    portprotected: int
    addressunprotected: str
    portunprotected: int
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


class PlayData(BaseModel):
    worlds: list[World]
    characters: list[Character]


class LoginResponse(BaseModel):
    session: Session
    playdata: PlayData
