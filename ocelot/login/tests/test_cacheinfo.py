from sqlalchemy.ext.asyncio import AsyncSession
from starlette.testclient import TestClient
import pytest

from ...models import OnlinePlayer


@pytest.mark.anyio
async def test_client_cacheinfo(client: TestClient, db_session: AsyncSession):
    async with db_session.begin():
        db_session.add_all(OnlinePlayer(player_id=i + 1) for i in range(3))

    res = client.post("/client", json={"type": "cacheinfo"})

    json = res.json()
    assert json["playersonline"] == 3
