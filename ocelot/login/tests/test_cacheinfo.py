import pytest
from databases import Database
from httpx import AsyncClient


@pytest.mark.anyio
async def test_client_cacheinfo(client: AsyncClient, database: Database):
    await database.execute(query="DELETE FROM players_online")

    await database.execute_many(
        query="INSERT INTO players_online (player_id) VALUES (:player_id)",
        values=[{"player_id": i + 1} for i in range(3)],
    )

    res = await client.post("/client", json={"type": "cacheinfo"})

    json = res.json()
    assert json["playersonline"] == 3
