import enum
from dataclasses import dataclass
from typing import Optional

from .ammunition import AmmunitionType, ShootType
from .mixins import LevelRestricted, LightEmitter, VocationRestricted
from .prototypes import Item


@enum.unique
class Skill(enum.Enum):
    FIST = enum.auto()
    SWORD = enum.auto()
    CLUB = enum.auto()
    AXE = enum.auto()
    DISTANCE = enum.auto()
    MAGIC = enum.auto()


@dataclass
class MeleeWeapon(Item, LevelRestricted, VocationRestricted):
    skill: Skill
    weight: int

    @property
    def range(self):
        return 1


@dataclass
class DistanceWeapon(Item, LevelRestricted, VocationRestricted):
    ammo_type: AmmunitionType
    extra_attack: int
    hit_chance: int
    weight: int

    @property
    def range(self):
        return 1

    @property
    def skill(self):
        return Skill.DISTANCE


@dataclass
class Throwable(Item, LevelRestricted, VocationRestricted):
    attack: int
    range: int
    weight: int

    break_chance: int
    max_hit_chance: int

    shoot_type: Optional[ShootType]

    @property
    def skill(self):
        return Skill.DISTANCE


@dataclass
class Wand(Item, LevelRestricted, LightEmitter, VocationRestricted):
    range: int
    weight: int

    mana_cost: int
    min_damage: int
    max_damage: int

    @property
    def skill(self):
        return Skill.MAGIC
