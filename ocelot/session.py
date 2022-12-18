import base64
import secrets
from abc import ABC, abstractmethod

from ocelot.config import _Session, _TFSSession, _TokenSession
from ocelot.models import Account


class SessionManager(ABC):
    @abstractmethod
    def encode(self, account: Account, *args) -> str:
        pass

    @abstractmethod
    async def decode(self, session_token: bytes) -> Account:
        pass


class TokenSessionManager(SessionManager):
    def __init__(self):
        self.tokens = {}

    def encode(self, account: Account, *args) -> str:
        token = secrets.token_bytes(21)
        self.tokens[token] = account.id
        return base64.b64encode(token).decode("ascii")

    async def decode(self, session_token: bytes) -> Account:
        account_id = self.tokens[base64.b64decode(session_token).decode("ascii")]
        return await Account.get(id=account_id)


class TFSSessionManager(SessionManager):
    def encode(self, account: Account, *args) -> str:
        return "\n".join((account.name, account.password, *args))

    async def decode(self, session_token: bytes) -> Account:
        account_name, password, token, timestamp = session_token.decode("ascii").split(
            "\n"
        )
        return await Account.get(name=account_name, password=password)


def session_from_config(session: _Session) -> SessionManager:
    match session:
        case _TokenSession(type="token"):
            return TokenSessionManager()
        case _TFSSession(type="tfs"):
            return TFSSessionManager()
        case _:
            raise ValueError(f"Invalid session configuration: {session}")
