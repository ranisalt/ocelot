import enum
from dataclasses import dataclass

from .mixins import LevelRestricted, VocationRestricted
from .prototypes import Item


@enum.unique
class AmmunitionType(enum.Enum):
    ARROW = "arrow"
    BOLT = "bolt"


@enum.unique
class ShootType(enum.Enum):
    BOLT = 2
    ARROW = 3
    POISON_ARROW = 6
    BURST_ARROW = 7
    POWER_BOLT = 14
    INFERNAL_BOLT = 16
    SNIPER_ARROW = 22
    ONYX_ARROW = 23
    PIERCING_BOLT = 24
    FLASH_ARROW = 33
    FLAMMING_ARROW = 34
    SHIVER_ARROW = 35
    EARTH_ARROW = 40
    TARSAL_ARROW = 44
    VORTEX_BOLT = 45
    PRISMATIC_BOLT = 48
    CRYSTALLINE_ARROW = 49
    DRILL_BOLT = 50
    ENVENOMED_ARROW = 51
    SIMPLE_ARROW = 54
    DIAMOND_ARROW = 57
    SPECTRAL_BOLT = 58


@dataclass
class Ammunition(Item, LevelRestricted, VocationRestricted):
    ammo_type: AmmunitionType
    shoot_type: ShootType
    weight: int

    attack_physical: int = 0
    attack_earth: int = 0
    attack_energy: int = 0
    attack_fire: int = 0
    attack_ice: int = 0

    max_hit_chance: int = 100
