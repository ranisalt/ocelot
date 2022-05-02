import sqlalchemy.orm
from fastapi.testclient import TestClient

from ...models import OnlinePlayer


def test_client_cacheinfo(client: TestClient, db_session: sqlalchemy.orm.sessionmaker):
    with db_session() as db:
        for i in range(3):
            db.add(OnlinePlayer(player_id=i + 1))
        db.commit()

    res = client.post("/client", json={"type": "cacheinfo"})

    json = res.json()
    assert json["playersonline"] == 3
