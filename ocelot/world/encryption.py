from struct import iter_unpack, pack_into
from typing import Generator, Iterable, Protocol, SupportsBytes, TypeVar


class EncryptionKey(Protocol):
    def encrypt(self, data: SupportsBytes) -> SupportsBytes:
        ...

    def decrypt(self, data: SupportsBytes) -> SupportsBytes:
        ...


class NoEncryption(EncryptionKey):
    def encrypt(self, data: SupportsBytes) -> SupportsBytes:
        return data

    def decrypt(self, data: SupportsBytes) -> SupportsBytes:
        return data


T = TypeVar("T")


def grouper(iterable: Iterable[T], n) -> Iterable[tuple[T, ...]]:
    "Collect data into non-overlapping fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3) --> ABC DEF
    args = [iter(iterable)] * n
    return zip(*args, strict=True)


class XteaKey(EncryptionKey):
    mask = 0xFFFFFFFF

    def __init__(self, key: bytes) -> None:
        self.key = tuple(grouper(self.expand_key(key), 2))
        assert len(self.key) == 32

    @staticmethod
    def expand_key(key: bytes) -> bytes:
        assert len(key) == 16

        k = [
            int.from_bytes(key[i : i + 4], byteorder="little") for i in range(0, 16, 4)
        ]
        sum, delta, mask = 0, 0x9E3779B9, 0xFFFFFFFF

        for _ in range(0, 32):
            yield (sum + k[sum & 3]) & mask
            sum = (sum + delta) & mask
            yield (sum + k[(sum >> 11) & 3]) & mask

    def encrypt(self, data: bytes) -> Generator[int, None, None]:
        r"""Encrypts data using the XTEA algorithm.

        >>> key = XteaKey(b'\x00' * 16)
        >>> [*key.encrypt(b'\x00\x00\x00\x00\x00\x00\x00\x00')]
        [222, 233, 212, 216, 247, 19, 30, 217]
        >>> [*key.encrypt(b'\x00\x00\x00\x00\x00\x00\x00\x01')]
        [71, 24, 100, 104, 209, 210, 52, 61]

        Test vectors from https://github.com/froydnj/ironclad/blob/fe88483bba68eac4db3b48bb4a5a40035965fc84/testing/test-vectors/xtea.testvec
        """

        assert len(data) % 8 == 0

        k, m = self.key, self.mask

        buf = bytearray(len(data))
        # buf = BytesIO()
        # buf = bytearray(data)
        v0: int
        v1: int
        # for i in range(0, len(buf), 8):
        for i, (v0, v1) in enumerate(iter_unpack(">II", data)):
            # for v0, v1 in iter_unpack(">II", data):
            # v0 = int.from_bytes(data[i : i + 4], byteorder="big")
            # v1 = int.from_bytes(data[i + 4 : i + 8], byteorder="big")

            for k0, k1 in k:
                v0 = (v0 + (((v1 << 4 ^ v1 >> 5) + v1) ^ k0)) & m
                v1 = (v1 + (((v0 << 4 ^ v0 >> 5) + v0) ^ k1)) & m

            # buf[i : i + 4] = v0.to_bytes(4, byteorder="big")
            # buf[i + 4 : i + 8] = v1.to_bytes(4, byteorder="big")
            pack_into(">II", buf, i * 8, v0, v1)
            # buf.write(pack(">II", v0, v1))

        return buf

    def decrypt(self, data: bytes) -> bytes:
        r"""Decrypts data using the XTEA algorithm.

        >>> key = XteaKey(b'\x00' * 16)
        >>> [*key.decrypt(b'\xde\xe9\xd4\xd8\xf7\x13\x1e\xd9')]
        [0, 0, 0, 0, 0, 0, 0, 0]
        >>> [*key.decrypt(b'\x47\x18\x64\x68\xd1\xd2\x34\x3d')]
        [0, 0, 0, 0, 0, 0, 0, 1]

        Test vectors from https://github.com/froydnj/ironclad/blob/fe88483bba68eac4db3b48bb4a5a40035965fc84/testing/test-vectors/xtea.testvec
        """

        assert len(data) % 8 == 0

        k, m = self.key, self.mask

        buf = bytearray(len(data))
        # buf = BytesIO()
        v0: int
        v1: int
        # for i in range(0, len(buf), 8):
        for i, (v0, v1) in enumerate(iter_unpack(">II", data)):
            # for v0, v1 in iter_unpack(">II", data):
            # v0 = int.from_bytes(data[i : i + 4], byteorder="big")
            # v1 = int.from_bytes(data[i + 4 : i + 8], byteorder="big")

            for k0, k1 in reversed(k):
                v1 = (v1 - (((v0 << 4 ^ v0 >> 5) + v0) ^ k1)) & m
                v0 = (v0 - (((v1 << 4 ^ v1 >> 5) + v1) ^ k0)) & m

            # buf[i : i + 4] = v0.to_bytes(4, byteorder="big")
            # buf[i + 4 : i + 8] = v1.to_bytes(4, byteorder="big")
            pack_into(">II", buf, i * 8, v0, v1)
            # buf.write(pack(">II", v0, v1))

        return buf
