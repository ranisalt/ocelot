from asyncio import StreamReader, StreamWriter
from io import SEEK_CUR, BytesIO
from typing import SupportsBytes
from zlib import adler32

from .encryption import EncryptionKey, NoEncryption


def adler32_checksum(data: bytes | bytearray) -> bytes:
    return adler32(data).to_bytes(4, byteorder="little")


class InputMessage:
    def __init__(self, data: BytesIO) -> None:
        self.data = data

    def read(self, length: int | None) -> bytes:
        return self.data.read(length)

    def read_byte(self, signed=False) -> int:
        return int.from_bytes(self.read(1), byteorder="little", signed=signed)

    def read_coords(self) -> tuple[int, int, int]:
        return (
            int.from_bytes(self.data.read(2), byteorder="little"),
            int.from_bytes(self.data.read(2), byteorder="little"),
            int.from_bytes(self.data.read(1), byteorder="little"),
        )

    def read_int(self, length: int, signed=False) -> int:
        return int.from_bytes(self.data.read(length), byteorder="little", signed=signed)

    def read_bytes(self) -> bytes:
        length = int.from_bytes(self.data.read(2), byteorder="little", signed=False)
        return self.data.read(length)

    def read_string(self) -> str:
        length = int.from_bytes(self.data.read(2), byteorder="little", signed=False)

        out = bytearray()
        while len(out) < length:
            next = self.read_byte()
            if next == 0xFD:
                next = self.read_byte()

            out.append(next)

        return out.decode("utf-8")

    def skip(self, length: int):
        self.data.seek(length, SEEK_CUR)


class OutputMessage:
    def __init__(self, packet_type: int) -> None:
        self.buffer = bytearray([packet_type])

    def add(self, value: SupportsBytes) -> None:
        self.buffer.extend(bytes(value))

    def add_byte(self, value: int) -> None:
        self.buffer.append(value)

    def add_int(self, value: int, length: int, signed=False) -> None:
        self.buffer.extend(value.to_bytes(length, byteorder="little", signed=signed))

    def add_string(self, value: str) -> None:
        self.buffer.extend(len(value).to_bytes(2, byteorder="little", signed=False))
        self.buffer.extend(value.encode("ascii"))

    def checksum(self) -> bytes:
        return adler32_checksum(self.buffer)

    def __bytes__(self) -> bytes:
        return bytes(self.buffer)

    def __len__(self) -> int:
        return len(self.buffer)


class Connection:
    def __init__(self, reader: StreamReader, writer: StreamWriter) -> None:
        self.reader = reader
        self.writer = writer
        self.encryption_key: EncryptionKey = NoEncryption()

    def set_encryption_key(self, key: EncryptionKey) -> None:
        self.encryption_key = key

    def __aiter__(self):
        return self

    async def __anext__(self) -> InputMessage:
        length = await self.read_int(2)
        if length == 0:
            raise StopAsyncIteration

        checksum = await self.read(4)
        data = await self.read(length - 4)
        return InputMessage(data)

    async def disconnect_client(self, message: str) -> None:
        output = OutputMessage(0x14)
        output.add_string(message)
        self.send(output)
        await self.disconnect()

    async def read_packet(self) -> InputMessage:
        length = await self.read_int(2)
        if length == 0:
            raise StopAsyncIteration

        checksum = await self.read(4)
        data = await self.read(length - 4)
        return InputMessage(data)

    async def read(self, length: int) -> bytes:
        return await self.reader.read(length)

    async def read_byte(self, signed: bool | None = None) -> int:
        b = await self.reader.read(1)
        return int.from_bytes(b, byteorder="little", signed=signed)

    async def read_int(self, length: int, signed: bool | None = None) -> int:
        b = await self.reader.read(length)
        return int.from_bytes(b, byteorder="little", signed=signed)

    async def read_string(self) -> bytes:
        length = await self.read_int(2)
        return await self.reader.read(length)

    def send(self, data: SupportsBytes) -> None:
        packet = bytes(self.encryption_key.encrypt(data))
        self.writer.write(packet)

    async def disconnect(self) -> None:
        await self.writer.drain()
        self.writer.close()
