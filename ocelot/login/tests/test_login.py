import hashlib
from datetime import datetime
from operator import itemgetter

import pytest
from faker import Faker
from httpx import AsyncClient

from ocelot import config
from ocelot.models import Account, Character, PlayerSex


@pytest.mark.anyio
async def test_login(
    client: AsyncClient,
    config: config.Config,
    faker: Faker,
    mocked_now: datetime,
):
    email, password = faker.email(), faker.password()
    password_hash = hashlib.sha1(password.encode("ascii")).hexdigest()

    account = await Account.create(name=email, password=password_hash)

    await Character.create(
        account=account,
        name="Bubble",
        level=273,
        vocation=8,
        sex=PlayerSex.Female,
        last_login_at=mocked_now.timestamp() - 3600,
    )
    await Character.create(
        account=account,
        name="Cachero",
        level=423,
        vocation=5,
        sex=PlayerSex.Male,
        last_login_at=mocked_now.timestamp() - 7200,
    )

    res = await client.post(
        "/login", json={"type": "login", "email": email, "password": password}
    )
    json = res.json()

    session = json["session"]
    expected_token = f"{email}\n{password}\n\n{int(mocked_now.timestamp())}"
    assert session["sessionkey"] == expected_token
    assert session["lastlogintime"] == mocked_now.timestamp() - 3600
    assert session["ispremium"] is False
    assert session["premiumuntil"] == 0

    default_world = config.worlds["default"]
    worlds: list[dict] = json["playdata"]["worlds"]
    assert len(worlds) == 1
    assert worlds[0]["id"] == default_world.id
    assert worlds[0]["name"] == default_world.name
    assert worlds[0]["pvptype"] == 0
    assert worlds[0]["externaladdressprotected"] == default_world.address_protected
    assert worlds[0]["externalportprotected"] == default_world.port_protected
    assert worlds[0]["externaladdressunprotected"] == default_world.address_unprotected
    assert worlds[0]["externalportunprotected"] == default_world.port_unprotected

    characters: list[dict] = sorted(
        json["playdata"]["characters"], key=itemgetter("name")
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


@pytest.mark.anyio
async def test_login_missing_email(client: AsyncClient, faker: Faker):
    res = await client.post(
        "/login", json={"type": "login", "password": faker.password()}
    )
    assert res.json()["errorCode"] == 3


@pytest.mark.anyio
async def test_login_missing_password(client: AsyncClient, faker: Faker):
    res = await client.post("/login", json={"type": "login", "email": faker.email()})
    assert res.json()["errorCode"] == 3


@pytest.mark.anyio
async def test_login_invalid_email(client: AsyncClient, faker: Faker):
    email, password = faker.email(), faker.password()
    password_hash = hashlib.sha1(password.encode("ascii")).hexdigest()

    await Account.create(name=email, password=password_hash)

    res = await client.post(
        "/login", json={"type": "login", "email": email[1:], "password": password}
    )
    assert res.json()["errorCode"] == 3


@pytest.mark.anyio
async def test_login_wrong_password(client: AsyncClient, faker: Faker):
    email, password = faker.email(), faker.password()
    password_hash = hashlib.sha1(password.encode("ascii")).hexdigest()

    await Account.create(name=email, password=password_hash)

    res = await client.post(
        "/login", json={"type": "login", "email": email, "password": password[1:]}
    )
    assert res.json()["errorCode"] == 3
