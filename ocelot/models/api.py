from typing import Callable

import sqlalchemy.orm
from fastapi import Request

SessionMaker = Callable[..., sqlalchemy.orm.Session]


def get_db(request: Request):
    session: SessionMaker = request.app.state.sessionmaker
    with session() as db:
        yield db
