from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key

from ..rsa import RSAKey


def test_rsa_encrypt():
    key = RSAKey(generate_private_key(public_exponent=65537, key_size=1024))

    encrypted = key.encrypt(b"Hello World!")
    decrypted = key.decrypt(encrypted)

    assert decrypted == b"\x00" * 116 + b"Hello World!"
