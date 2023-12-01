import datetime
import hashlib
import re
import string
from typing import Callable

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from tortoise.transactions import in_transaction

from ocelot.config import Config, pvp_index_to_display_name, pvp_type_to_index
from ocelot.models import Account, Character, OnlinePlayer, PlayerSex

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


def normalize_body(body: dict[str, str]):
    return {key.lower(): value for key, value in body.items()}


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


async def accounts(request: Request):
    body = await request.json()

    # there is an inconsistency with casing in these routes
    match body.get("type", body.get("Type")):
        case "getaccountcreationstatus":
            config: Config = request.app.state.config
            world = next(world for world in config.worlds.values())

            return JSONResponse(
                {
                    "Worlds": [
                        {
                            "Name": world.name,
                            "PlayersOnline": 345,
                            "CreationDate": 1697616000,
                            "Region": "South America",
                            "PvPType": pvp_index_to_display_name[
                                pvp_type_to_index[world.pvp]
                            ],
                            "PremiumOnly": 1,
                            "TransferType": "Blocked",
                            "BattlEyeActivationTimestamp": 1697616000,
                            "BattlEyeInitiallyActive": 1,
                        }
                    ],
                    "RecommendedWorld": world.name,
                    "IsCaptchaDeactivated": False,
                }
            )

        case "GenerateCharacterName":
            generate_name: Callable[[], str] = request.app.state.generate_name
            return JSONResponse({"GeneratedName": generate_name()})

        case "CheckEMail":
            email = body.get("Email", "")
            if not email:
                return error_response(
                    ErrorCode.ACCOUNT_CREATION_EMPTY_EMAIL, EMail=email
                )

            if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
                return error_response(
                    ErrorCode.ACCOUNT_CREATION_INVALID_EMAIL, EMail=email
                )

            return JSONResponse({"IsValid": True, "EMail": email})

        case "checkpassword":
            password1 = body.get("Password1", "")
            if not password1:
                return error_response(
                    ErrorCode.CHECK_PASSWORD_EMPTY_PASSWORD, Password1=email
                )

            # "PasswordStrength": 0,
            # "PasswordStrengthColor": "#EC644B",

            # "PasswordStrength": 1,
            # "PasswordStrengthColor": "#EC644B",

            # "PasswordStrength": 2,
            # "PasswordStrengthColor": "#eb8005",

            # "PasswordStrength": 3,
            # "PasswordStrengthColor": "#b0b300",

            # "PasswordStrength": 4,
            # "PasswordStrengthColor": "#20a000",

            config: Config = request.app.state.config
            min_len = config.universe.minimum_password_length

            # valid_symbols = "!@#$%&*()_-+=;:.>,<\"'\\|{[}]"
            valid_characters = f"{string.ascii_letters}{string.digits}{string.punctuation}"

            return JSONResponse(
                {
                    "PasswordRequirements": {
                        "PasswordLength": len(password1) >= min_len,
                        "InvalidCharacters": all(c in valid_characters for c in password1),
                        "HasLowerCase": any(c in string.ascii_lowercase for c in password1),
                        "HasUpperCase": any(c in string.ascii_uppercase for c in password1),
                        "HasNumber": any(c in string.digits for c in password1),
                    },
                    "Password1": password1,
                    "PasswordStrength": 2,
                    "PasswordStrengthColor": "#eb8005",
                    "PasswordValid": True,
                }
            )

        case "CreateAccountAndCharacter":
            character_name = body.get("CharacterName", "")
            if not character_name:
                return JSONResponse(
                    {
                        "errorCode": None,
                        "errorMessage": "Please enter a name for your character!",
                        "CharacterName": character_name,
                        "Success": False,
                    }
                )

            character_sex = body.get("CharacterSex")
            if not character_sex:
                return error_response(
                    ErrorCode.ACCOUNT_CREATION_INTERNAL_ERROR,
                    Success=False,
                    IsRecaptcha2Requested=None,
                )

            # client_type = body['ClientType'] # 'client'
            email = body.get("EMail", "")
            if not email:
                return error_response(
                    ErrorCode.ACCOUNT_CREATION_EMPTY_EMAIL, EMail=email, Success=False
                )

            password = body.get("Password")
            if not password:
                return error_response(
                    ErrorCode.ACCOUNT_CREATION_PASSWORD_DOES_NOT_MEET_REQUIREMENTS,
                    PasswordValid=False,
                    Success=False,
                )

            # recaptcha2_token = body['ReCaptcha2Token']
            # recaptcha3_token = body['ReCaptcha3Token']

            selected_world = body.get("SelectedWorld")
            if not selected_world:
                return error_response(
                    ErrorCode.ACCOUNT_CREATION_INTERNAL_ERROR,
                    Success=False,
                    IsRecaptcha2Requested=None,
                )

            password_hash = hashlib.sha1(password.encode("ascii")).hexdigest()

            async with in_transaction():
                account = await Account.create(name=email, password=password_hash)
                await Character.create(
                    name=character_name,
                    sex=PlayerSex.Male if character_sex == "male" else PlayerSex.Female,
                    account=account,
                )

            return JSONResponse({})

        case _:  # pragma: no cover
            return error_response(ErrorCode.INTERNAL_ERROR)


async def wildcard(request: Request):
    body = await request.body()

    print(request.method, request.url)
    print("headers:", request.headers)
    print(body)

    return error_response(ErrorCode.INTERNAL_ERROR)


routes = [
    Route("/login", login, methods=["POST"]),
    Route("/client", client, methods=["POST"]),
    Route(
        "/accounts",
        accounts,
        methods=["POST"],
    ),
    Route("/{path:path}", wildcard, methods=["GET", "POST"]),
]
