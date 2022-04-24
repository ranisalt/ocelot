import hashlib
from datetime import datetime
from operator import itemgetter

from faker import Faker
from flask.testing import FlaskClient
from pony.orm import db_session

from ..config import Config
from ..database import Account, Character
from ..enums import PlayerSex
from ..routes import pvp_type_to_index


def test_login(client: FlaskClient, config: Config, mocked_now: datetime, faker: Faker):
    email, password = faker.email(), faker.password()
    password_hash = hashlib.sha1(password.encode("ascii")).hexdigest()

    with db_session:
        account = Account(name=email, password=password_hash)
        Character(
            account=account, name="Bubble", level=273, vocation=8, sex=PlayerSex.Female
        ),
        Character(
            account=account, name="Cachero", level=423, vocation=5, sex=PlayerSex.Male
        ),

    res = client.post(
        "/login", json={"type": "login", "email": email, "password": password}
    )
    assert res.status_code == 200
    assert res.json

    session = res.json["session"]
    expected_token = f"{email}\n{password}\n\n{int(mocked_now.timestamp())}"
    assert session["sessionkey"] == expected_token
    assert session["lastlogintime"] == 0
    assert session["ispremium"] is False
    assert session["premiumuntil"] == 0

    default_world = config.worlds["default"]
    worlds: list[dict] = res.json["playdata"]["worlds"]
    assert len(worlds) == 1
    assert worlds[0]["id"] == default_world.id
    assert worlds[0]["name"] == default_world.name
    assert worlds[0]["pvp-type"] == pvp_type_to_index[default_world.pvp]
    assert worlds[0]["address-protected"] == default_world.address_protected
    assert worlds[0]["port-protected"] == default_world.port_protected
    assert worlds[0]["address-unprotected"] == default_world.address_unprotected
    assert worlds[0]["port-unprotected"] == default_world.port_unprotected

    characters: list[dict] = sorted(
        res.json["playdata"]["characters"], key=itemgetter("name")
    )
    assert len(characters) == 2

    assert characters[0]["worldid"] == default_world.id
    assert characters[0]["name"] == "Bubble"
    assert characters[0]["level"] == 273
    assert characters[0]["vocation"] == "Elite Knight"
    assert not characters[0]["ismale"]
    assert characters[1]["worldid"] == default_world.id
    assert characters[1]["name"] == "Cachero"
    assert characters[1]["level"] == 423
    assert characters[1]["vocation"] == "Master Sorcerer"
    assert characters[1]["ismale"]


def test_login_missing_email(client: FlaskClient, faker: Faker):
    res = client.post("/login", json={"type": "login", "password": faker.password()})
    assert res.json and res.json["errorCode"] == 3


def test_login_missing_password(client: FlaskClient, faker: Faker):
    res = client.post("/login", json={"type": "login", "email": faker.email()})
    assert res.json and res.json["errorCode"] == 3


def test_login_invalid_email(client: FlaskClient, faker: Faker):
    email, password = faker.email(), faker.password()
    password_hash = hashlib.sha1(password.encode("ascii")).hexdigest()

    with db_session:
        Account(name=email, password=password_hash)

    res = client.post(
        "/login", json={"type": "login", "email": email[1:], "password": password}
    )
    assert res.json and res.json["errorCode"] == 3


def test_login_wrong_password(client: FlaskClient, faker: Faker):
    email, password = faker.email(), faker.password()
    password_hash = hashlib.sha1(password.encode("ascii")).hexdigest()

    with db_session:
        Account(name=email, password=password_hash)

    res = client.post(
        "/login", json={"type": "login", "email": email, "password": password[1:]}
    )
    assert res.json and res.json["errorCode"] == 3
