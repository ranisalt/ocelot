import pytest
from httpx import AsyncClient

from ocelot.models import OnlinePlayer


@pytest.mark.anyio
async def test_client_cacheinfo(client: AsyncClient):
    await OnlinePlayer.bulk_create(OnlinePlayer(player_id=i + 1) for i in range(3))

    res = await client.post("/client", json={"type": "cacheinfo"})

    json = res.json()
    assert json["playersonline"] == 3
