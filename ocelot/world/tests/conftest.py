from asyncio import Server, StreamWriter, open_connection, start_server
from codecs import StreamReader

import pytest

from ..connection import Connection


class MockServer:
    def __init__(self) -> None:
        self.connection: Connection | None = None
        self.server: Server | None = None

    async def open_connection(self):
        socket = self.server.sockets[0]
        return await open_connection(*socket.getsockname())

    async def __aenter__(self):
        def on_connect(reader, writer):
            self.connection = Connection(reader, writer)

        self.server = await start_server(on_connect, "127.0.0.1", 7171)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.server.close()
        await self.server.wait_closed()


@pytest.fixture
async def server():
    async with MockServer() as server:
        yield server


_Connection = tuple[StreamReader, StreamWriter, Connection]


@pytest.fixture
async def _connection(server: MockServer):
    reader, writer = await server.open_connection()
    yield reader, writer, server.connection


@pytest.fixture
def connection(_connection: _Connection):
    _, _, connection = _connection
    return connection


@pytest.fixture
def reader(_connection: _Connection):
    reader, _, _ = _connection
    return reader


@pytest.fixture
def writer(_connection: _Connection):
    _, writer, _ = _connection
    return writer
