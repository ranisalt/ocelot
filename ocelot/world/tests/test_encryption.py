from secrets import randbits

from ..encryption import XteaKey

data = b"\x00" * 24584
# data = b"\x00" * 8


def test_xtea_encrypt(benchmark):
    key = XteaKey(randbits(128).to_bytes(16, byteorder="little"))

    result = benchmark(key.encrypt, data)
    assert bytes(key.decrypt(result)) == data


def test_xtea_decrypt(benchmark):
    key = XteaKey(randbits(128).to_bytes(16, byteorder="little"))

    result = benchmark(key.decrypt, data)
    assert bytes(key.encrypt(result)) == data
