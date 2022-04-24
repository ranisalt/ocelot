from flask.testing import FlaskClient
from pony.orm import db_session

from ..database import OnlinePlayer


def test_client_cacheinfo(client: FlaskClient):
    with db_session:
        for i in range(3):
            OnlinePlayer(player_id=i)

    res = client.post("/client", json={"type": "cacheinfo"})

    assert res.json
    assert res.json["playersonline"] == 3
