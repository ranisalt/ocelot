import pytest

from ..connection import OutputMessage
from ..position import Position


@pytest.mark.anyio
def test_outputmessage_add_byte():
    packet = OutputMessage(0x00)
    packet.add_byte(0x01)

    assert bytes(packet) == b"\x00\x01", "data does not match"


@pytest.mark.anyio
def test_outputmessage_add_int():
    packet = OutputMessage(0x00)
    packet.add_int(0x01, 1)
    assert bytes(packet) == b"\x00\x01", "data does not match"

    packet = OutputMessage(0x00)
    packet.add_int(0x0102, 2)
    assert bytes(packet) == b"\x00\x02\x01", "data does not match"

    packet = OutputMessage(0x00)
    packet.add_int(0x01020304, 4)
    assert bytes(packet) == b"\x00\x04\x03\x02\x01", "data does not match"


@pytest.mark.anyio
def test_outputmessage_add_string():
    packet = OutputMessage(0x00)
    packet.add_string("Hello, world!")

    assert bytes(packet) == b"\x00\x0d\x00Hello, world!", "data does not match"


@pytest.mark.anyio
def test_outputmessage_add_position():
    packet = OutputMessage(0x00)
    position = Position(x=1, y=2, z=3)
    packet.add(position)

    assert bytes(packet) == b"\x00\x01\x00\x02\x00\x03", "data does not match"
