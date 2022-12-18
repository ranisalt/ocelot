from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .map import Map
    from .position import Position


class Creature:
    def __init__(self, position: "Position") -> None:
        self.position = position
        self.spectators: list[Creature] = []

    def on_creature_appear(self, creature: "Creature") -> None:
        self.spectators.append(creature)

    def on_spawn(self, map: "Map"):
        pass
