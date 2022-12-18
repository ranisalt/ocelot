import enum
from dataclasses import dataclass
from typing import Optional

from .mixins import Decays, LightEmitter
from .prototypes import Item


@enum.unique
class FloorChange(enum.Flag):
    DOWN = 1 << 0
    NORTH = 1 << 1
    SOUTH = 1 << 2
    EAST = 1 << 3
    WEST = 1 << 4
    SOUTH_ALT = 1 << 5
    EAST_ALT = 1 << 6


class Fluid(enum.Enum):
    EMPTY = 0
    BLUE = 1
    RED = 2
    BROWN = 3
    GREEN = 4
    YELLOW = 5
    WHITE = 6
    PURPLE = 7
    BLACK = 8

    NONE = EMPTY
    WATER = BLUE
    BLOOD = RED
    BEER = BROWN
    SLIME = GREEN
    LEMONADE = YELLOW
    MILK = WHITE
    MANA = PURPLE
    INK = BLACK

    LIFE = RED + 8
    OIL = BROWN + 8
    URINE = YELLOW + 8
    COCONUT_MILK = WHITE + 8
    WINE = PURPLE + 8

    MUD = BROWN + 16
    FRUIT_JUICE = YELLOW + 16

    LAVA = RED + 24
    RUM = BROWN + 24
    SWAMP = GREEN + 24

    TEA = BROWN + 32

    MEAD = BROWN + 40


@dataclass
class Ground(Item, Decays, LightEmitter):
    floor_change: Optional[FloorChange]
    fluid_source: Optional[Fluid]
    speed: int
    ...
