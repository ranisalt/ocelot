from typing import Optional

from flask import Blueprint, current_app, request
from pony import orm

from . import handlers
from .database import OnlinePlayer
from .errors import (
    ErrorCode,
    InternalError,
    InvalidCredentials,
    OcelotError,
    error_response,
)

router = Blueprint("login", __name__)

cacheinfo_defaults = {
    "twitchstreams": 0,
    "twitchviewer": 0,
    "gamingyoutubestreams": 0,
    "gamingyoutubeviewer": 0,
}


@router.errorhandler(OcelotError)
def handle_invalid_credentials(error: OcelotError):
    return error_response(error.code)


@router.post("/login")
@router.post("/login.php")
def login():
    match type_ := request.json["type"]:
        case "login":
            email: Optional[str] = request.json.get("email")
            password: Optional[str] = request.json.get("password")

            if not email or not password:
                raise InvalidCredentials

            # optional in otclient
            # stay_logged_in: bool = request.json.get("stayloggedin", False)
            token: str = request.json.get("token", "")

            resp = handlers.login(current_app.config["OCELOT"], email, password, token)
            return resp.dict()

        case _:  # pragma: no cover
            print(type_)
            raise InternalError


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
            print(type_)
            return error_response(ErrorCode.INTERNAL_ERROR)


# @router.post("/", defaults={"path": ""})
# @router.post("/<path:path>")
# def catch_all(path):
#     print(f"{request.method} /{path} {request.json}")
