from asyncio import StreamReader, StreamWriter

import pytest

from ..connection import Connection, OutputMessage


@pytest.mark.anyio
async def test_connection_read_int(connection: Connection, writer: StreamWriter):
    writer.write(b"\x01")
    assert await connection.read_int(1) == 0x01, "value should be 0x01"

    writer.write(b"\x02\x01")
    assert await connection.read_int(2) == 0x0102, "value should be 0x0102"

    writer.write(b"\x04\x03\x02\x01")
    assert await connection.read_int(4) == 0x01020304, "value should be 0x01020304"


@pytest.mark.anyio
async def test_connection_read_string(connection: Connection, writer: StreamWriter):
    writer.write(b"\x0d\x00Hello, world!")
    assert await connection.read_string() == b"Hello, world!", "data does not match"


@pytest.mark.anyio
async def test_connection_send(connection: Connection, reader: StreamReader):
    packet = OutputMessage(0x00)
    packet.add_string("Hello, world!")
    connection.send(packet)

    assert await reader.read(16) == b"\x00\x0d\x00Hello, world!", "data does not match"


@pytest.mark.anyio
async def test_connection_disconnect_client(
    connection: Connection, reader: StreamReader
):
    await connection.disconnect_client("Hello, world!")

    assert await reader.read(1) == b"\x14", "opcode does not match"
    assert await reader.read(2) == b"\x0d\x00", "length does not match"
    assert await reader.read(13) == b"Hello, world!", "data does not match"
    # TODO: assert that the connection is closed
