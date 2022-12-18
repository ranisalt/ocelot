from io import SEEK_CUR, BytesIO


class Stream:
    def __init__(self, data: bytes):
        self.stream = BytesIO(data)

    def read(self, length: int | None) -> bytes:
        return self.stream.read(length)

    def read_byte(self, signed=False) -> int:
        return int.from_bytes(self.read(1), byteorder="little", signed=signed)

    def read_coords(self) -> tuple[int, int, int]:
        return (
            int.from_bytes(self.stream.read(2), byteorder="little"),
            int.from_bytes(self.stream.read(2), byteorder="little"),
            int.from_bytes(self.stream.read(1), byteorder="little"),
        )

    def read_int(self, length: int, signed=False) -> int:
        return int.from_bytes(
            self.stream.read(length), byteorder="little", signed=signed
        )

    def read_bytes(self) -> bytes:
        length = int.from_bytes(self.stream.read(2), byteorder="little", signed=False)
        return self.stream.read(length)

    def read_string(self) -> str:
        length = int.from_bytes(self.stream.read(2), byteorder="little", signed=False)

        out = bytearray()
        while len(out) < length:
            next = self.read_byte()
            if next == 0xFD:
                next = self.read_byte()

            out.append(next)

        return out.decode("utf-8")

    def skip(self, length: int):
        self.stream.seek(length, SEEK_CUR)
