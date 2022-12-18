from dataclasses import dataclass
from os import PathLike
from typing import BinaryIO, Sequence


@dataclass(slots=True)
class Node:
    type: int
    props: bytes
    children: Sequence["Node"]


def parse_otb_tree(stream: BinaryIO) -> Node:
    type_, *_ = stream.read(1)
    props = bytearray()
    children: list[Node] = []

    while byte := stream.read(1):
        match byte:
            case b"\xFD":  # escape
                assert len(children) == 0
                props.extend(stream.read(1))

            case b"\xFE":  # start
                children.append(parse_otb_tree(stream))

            case b"\xFF":  # end
                return Node(type=type_, props=bytes(props), children=tuple(children))

            case _:
                assert len(children) == 0
                props.extend(byte)

    raise ValueError("Unexpected end of file.")


def parse_otb(path: str, expected_identifier: bytes) -> Node:
    with open(path, "rb") as stream:
        identifier = stream.read(4)
        if identifier != b"\0\0\0\0" and identifier != expected_identifier:
            raise ValueError("Invalid magic header.")

        start = stream.read(1)
        assert start == b"\xFE", "Invalid first byte."

        return parse_otb_tree(stream)
