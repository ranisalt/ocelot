from typing import TYPE_CHECKING

from .connection import Connection, OutputMessage
from .creature import Creature

if TYPE_CHECKING:
    from ocelot.models import Character

    from .map import Map
    from .position import Position


class Player(Creature):
    def __init__(
        self, character: "Character", connection: Connection, position: "Position"
    ) -> None:
        super().__init__(position=position)
        self.character = character
        self.connection = connection

    def on_creature_appear(self, creature: Creature) -> None:
        super().on_creature_appear(creature)

        packet = OutputMessage(0x69)
        packet.add(creature.position)

        self.connection.send(packet)

    def on_spawn(self, map: "Map"):
        super().on_spawn(map)

        for spectator in map.get_spectators(self.position):
            self.spectators.append(spectator)
            spectator.on_creature_appear(self)
