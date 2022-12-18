from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Position:
    x: int
    y: int
    z: int

    def __bytes__(self) -> bytes:
        return bytes(
            [
                *self.x.to_bytes(2, byteorder="little"),
                *self.y.to_bytes(2, byteorder="little"),
                *self.z.to_bytes(1, byteorder="little"),
            ]
        )
