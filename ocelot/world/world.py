import secrets
from asyncio import StreamReader, StreamWriter
from datetime import datetime
from typing import TYPE_CHECKING, Generator, Iterable
from zlib import adler32

from ocelot.stream import Stream

from .connection import Connection
from .encryption import XteaKey
from .player import Player

if TYPE_CHECKING:
    from ocelot.models import Account
    from ocelot.rsa import RSAKey
    from ocelot.session import SessionManager

    from .map import Map


def add_checksum_header(packet: Iterable[int]) -> Generator[int, None, None]:
    data = bytes(packet)

    length = len(data) + 4
    yield from length.to_bytes(2, byteorder="little")
    yield from adler32(data).to_bytes(4, byteorder="little")
    yield from data


class World:
    def __init__(
        self,
        id: int,
        name: str,
        private_key: "RSAKey",
        session_manager: "SessionManager",
        map: "Map",
        **kwargs
    ) -> None:
        self.id = id
        self.name = name
        self.private_key = private_key
        self.session_manager = session_manager
        self.map = map

        self.players_online: list[Player] = []

    async def on_connect(self, reader: StreamReader, writer: StreamWriter) -> None:
        world_name = await reader.readline()

        if world_name.removesuffix(b"\n") != self.name.encode("ascii"):
            # await connection.disconnect_client("Wrong world name.")
            return

        # challenge
        now = datetime.now()
        challenge_timestamp = int(now.timestamp()).to_bytes(4, byteorder="little")
        challenge_nonce = secrets.randbits(8)

        output = bytes((0x06, 0x00, 0x1F, *challenge_timestamp, challenge_nonce))
        writer.write(bytes(add_checksum_header(output)))

        connection = Connection(reader, writer)
        await self.handshake(connection, challenge_timestamp, challenge_nonce)

    async def handshake(
        self, connection: Connection, challenge_timestamp: bytes, challenge_nonce: int
    ) -> None:
        initial_packet = await connection.read_packet()

        protocol_id = initial_packet.read_byte()
        operating_system = initial_packet.read_int(2)
        protocol_version = initial_packet.read_int(2)
        client_version = initial_packet.read_int(4)
        if protocol_version < 1302:
            await connection.disconnect_client(
                "Only clients with protocol 13.02 allowed!"
            )
            return

        version_string = initial_packet.read_string()
        dat_revision = initial_packet.read_int(2)
        preview_state = initial_packet.read_byte()

        # # rsa decrypt
        # bytes_read = 16 + len(version_string)
        # bytes_remaining = length - bytes_read
        # if bytes_remaining < 128:
        #     await connection.disconnect()
        #     return

        remaining = initial_packet.read(128)
        if len(remaining) < 128:
            await connection.disconnect()
            return

        # symmetric key exchange
        payload = Stream(self.private_key.decrypt(remaining))
        if payload.read(1) != b"\x00":
            await connection.disconnect()
            return

        xtea_key = payload.read(16)
        connection.set_encryption_key(XteaKey(key=xtea_key))

        gamemaster = payload.read(1)

        session_key = payload.read_bytes()
        character_name = payload.read_bytes()

        timestamp = payload.read(4)
        if timestamp != challenge_timestamp:
            await connection.disconnect()
            return

        nonce = int.from_bytes(payload.read(1), byteorder="little")
        if nonce != challenge_nonce:
            await connection.disconnect()
            return

        account = await self.session_manager.decode(session_key)
        if not account:
            await connection.disconnect_client(
                "Account name or password is not correct."
            )
            return

        # successful login
        await self.login(
            connection=connection,
            character_name=character_name.decode("ascii"),
            account=account,
            operating_system=operating_system,
        )

    def add_player(self, player: Player) -> None:
        self.map.place_creature(player)
        self.players_online.append(player)

    async def login(
        self,
        connection: Connection,
        character_name: str,
        account: "Account",
        operating_system: int,
    ) -> None:
        character = await account.characters.filter(name=character_name).first()
        if not character:
            await connection.disconnect_client("Your character could not be loaded.")
            return

        player = Player(character=character, connection=connection)
        self.add_player(player)

        async for packet in connection:
            # todo: packet handling
            pass
