import xml.etree.ElementTree as ET
from dataclasses import dataclass
from os import PathLike
from typing import Generator

from ocelot.world.map import Position


@dataclass(slots=True)
class House:
    id: int
    town_id: int
    name: str
    door_position: Position
    rent: int
    size: int


def load_houses(path: PathLike) -> Generator[House, None, None]:
    tree = ET.parse(path)

    root = tree.getroot()
    assert root.tag == "houses"

    for element in root:
        assert element.tag == "house"

        id = int(element.get("houseid"))
        town_id = int(element.get("townid"))
        name = element.get("name")
        assert name

        entryx = int(element.get("entryx"))
        entryy = int(element.get("entryy"))
        entryz = int(element.get("entryz"))

        rent = int(element.get("rent"))
        size = int(element.get("size"))

        yield House(
            id=id,
            town_id=town_id,
            name=name,
            door_position=Position(x=entryx, y=entryy, z=entryz),
            rent=rent,
            size=size,
        )
