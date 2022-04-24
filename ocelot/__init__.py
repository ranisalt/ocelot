import os

from .config import Config

__version__ = "0.1.0"


def database_from_env(config: Config) -> str:
    if dsn := os.environ.get("DATABASE_URL"):
        return dsn

    if db := config.database:
        return f"mysql://{db.username}:{db.password}@{db.host}:{db.port}/{db.name}"

    db_host = os.environ.get("MYSQL_HOST", "localhost")
    db_port = int(os.environ.get("MYSQL_PORT", "3306"))

    db_user = os.environ.get("MYSQL_USER")
    assert db_user is not None, "MYSQL_USER not set"
    assert db_user != "root", "MYSQL_USER must not be 'root'"

    db_pass = os.environ.get("MYSQL_PASSWORD")
    assert db_pass is not None, "MYSQL_PASSWORD not set"

    db_name = os.environ.get("MYSQL_DATABASE", "forgottenserver")
    return f"mysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
