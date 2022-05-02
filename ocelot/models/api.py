from . import Session


def get_db():
    with Session() as session:
        yield session
