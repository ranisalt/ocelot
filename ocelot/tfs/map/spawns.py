import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from os import PathLike
from typing import Generator, Literal, Sequence

from ocelot.world.map import Position


@dataclass(slots=True)
class Monster:
    name: str
    chance: int


@dataclass(slots=True)
class Spawn:
    type: Literal["monster", "npc"]
    position: Position
    spawn_time: int
    direction: int
    monsters: Sequence[Monster] = field(default_factory=tuple)


def load_spawns(path: str) -> Generator[Spawn, None, None]:
    tree = ET.parse(path)

    root = tree.getroot()
    assert root.tag == "spawns"

    for element in root:
        assert element.tag == "spawn"

        centerx = int(element.get("centerx"))
        centery = int(element.get("centery"))
        # centerz = int(element.get("centerz"))  # unused, spawn z is absolute
        # radius = int(element.get("radius"))  # unused

        for child in element:
            match child.tag:
                case "monster" | "npc":
                    name = child.get("name")
                    assert name

                    x = int(child.get("x")) + centerx
                    y = int(child.get("y")) + centery
                    z = int(child.get("z"))

                    spawn_time = int(child.get("spawntime"))
                    direction = int(child.get("direction", "0"))

                    yield Spawn(
                        child.tag,
                        Position(x, y, z),
                        spawn_time,
                        direction,
                        monsters=(Monster(name, 1),),
                    )

                case "monsters":
                    x = int(child.get("x")) + centerx
                    y = int(child.get("y")) + centery
                    z = int(child.get("z"))

                    spawn_time = int(child.get("spawntime"))

                    monsters = []
                    for monster in child:
                        assert monster.tag == "monster"

                        name = monster.get("name")
                        assert name

                        chance = int(monster.get("chance"))
                        monsters.append(Monster(name, chance))

                    yield Spawn(
                        "monster",
                        Position(x, y, z),
                        spawn_time,
                        0,
                        tuple(monsters),
                    )

                case _:
                    raise ValueError(f"Invalid spawn element: {child.tag}")
