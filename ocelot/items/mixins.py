from dataclasses import dataclass
from typing import Optional


@dataclass
class Decays:
    decay_to: Optional[int]
    duration: Optional[int]


@dataclass
class LevelRestricted:
    min_level: Optional[int]


@dataclass
class LightEmitter:
    light_color: Optional[int]
    light_level: Optional[int]


@dataclass
class VocationRestricted:
    vocations: Optional[set[str]]
