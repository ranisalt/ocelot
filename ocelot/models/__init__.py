import enum

import sqlalchemy
import sqlalchemy.orm

mapper_registry: sqlalchemy.orm.registry = sqlalchemy.orm.registry()


class PlayerSex(enum.IntEnum):
    Female = 0
    Male = 1


@mapper_registry.mapped
class Account:
    __tablename__ = "accounts"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(32), unique=True)
    password = sqlalchemy.Column(sqlalchemy.String(40))
    # secret = Optional(str)
    premium_ends_at = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    # email = sqlalchemy.Column(sqlalchemy.String)

    characters: list["Character"] = sqlalchemy.orm.relationship("Character")

    @property
    def last_login(self) -> int:
        return max(c.last_login or 0 for c in self.characters)


@mapper_registry.mapped
class Character:
    __tablename__ = "players"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), unique=True)
    level = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    account_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("accounts.id"), nullable=False
    )
    vocation = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    look_type = sqlalchemy.Column("looktype", sqlalchemy.Integer, default=136)
    look_head = sqlalchemy.Column("lookhead", sqlalchemy.Integer, default=0)
    look_body = sqlalchemy.Column("lookbody", sqlalchemy.Integer, default=0)
    look_legs = sqlalchemy.Column("looklegs", sqlalchemy.Integer, default=0)
    look_feet = sqlalchemy.Column("lookfeet", sqlalchemy.Integer, default=0)
    look_addons = sqlalchemy.Column("lookaddons", sqlalchemy.Integer, default=0)
    sex = sqlalchemy.Column(sqlalchemy.Integer)
    last_login = sqlalchemy.Column("lastlogin", sqlalchemy.Integer, default=0)

    # account: Account = sqlalchemy.orm.relationship("Account", back_populates="characters")


@mapper_registry.mapped
class OnlinePlayer:
    __tablename__ = "players_online"

    player_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)


engine = sqlalchemy.create_engine("sqlite:///:memory:")
Session = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


# def dsn_from_env(config: Config) -> str:
#     # database_debug = os.environ.get("DATABASE_DEBUG")
#     # echo = database_debug is not None and database_debug[0] in "1tTyY"

#     if dsn := os.environ.get("DATABASE_URL"):
#         return dsn

#     if db := config.database:
#         return (
#             f"mysql+pymysql://{db.username}:{db.password}@{db.host}:{db.port}/{db.name}"
#         )

#     db_host = os.environ.get("MYSQL_HOST", "localhost")
#     db_port = int(os.environ.get("MYSQL_PORT", "3306"))

#     db_user = os.environ.get("MYSQL_USER")
#     assert db_user is not None, "MYSQL_USER not set"
#     assert db_user != "root", "MYSQL_USER must not be 'root'"

#     db_pass = os.environ.get("MYSQL_PASSWORD")
#     assert db_pass is not None, "MYSQL_PASSWORD not set"

#     db_name = os.environ.get("MYSQL_DATABASE", "forgottenserver")
#     return f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
