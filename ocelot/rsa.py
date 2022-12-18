from io import BytesIO

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey


class RSAKey:
    def __init__(self, key: RSAPrivateKey) -> None:
        self.d = key.private_numbers().d
        self.e = key.public_key().public_numbers().e
        self.n = key.public_key().public_numbers().n
        self.hash_size = key.key_size // 8

    def decrypt(self, ciphertext: bytes) -> bytes:
        message = pow(int.from_bytes(ciphertext, "big"), self.d, self.n)
        return message.to_bytes(self.hash_size, byteorder="big")

    def encrypt(self, message: bytes) -> bytes:
        ciphertext = pow(int.from_bytes(message, "big"), self.e, self.n)
        return ciphertext.to_bytes(self.hash_size, byteorder="big")

    @classmethod
    def from_pem(cls, data: bytes) -> "RSAKey":
        from cryptography.hazmat.primitives import serialization

        return cls(serialization.load_pem_private_key(data, password=None))


del RSAPrivateKey

__all__ = ["RSAKey"]
