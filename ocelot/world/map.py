from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, Mapping, Sequence

from .position import Position

if TYPE_CHECKING:
    from .creature import Creature


@dataclass(frozen=True, slots=True)
class Town:
    id: int
    name: str
    temple_position: Position


class Item:
    pass


class Tile:
    def __init__(self, ground_item: int):
        self.ground_item = ground_item

        self.creatures: list["Creature"] = []
        self.items: list[Item] = []

    def add_creature(self, creature: "Creature"):
        self.creatures.append(creature)

    def add_item(self, item: Item):
        self.items.append(item)

    def on_creature_appear(self) -> None:
        pass


class Map:
    def __init__(self, tiles: Mapping[Position, Tile], towns: Sequence[Town]):
        self.creatures: Sequence["Creature"] = []
        self.tiles = tiles
        self.towns = towns

    def get_spectators(self, position: Position) -> Iterable["Creature"]:
        for dx in range(-8, 9):
            for dy in range(-6, 7):
                for dz in range(-2, 3):
                    tile = self.tiles.get(
                        Position(position.x + dx, position.y + dy, position.z + dz)
                    )

                    if tile is not None:
                        yield from tile.creatures

    def place_creature(self, creature: "Creature"):
        self.tiles[creature.position].add_creature(creature)
        creature.on_spawn(self)
