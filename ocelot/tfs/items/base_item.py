from dataclasses import dataclass
from typing import Optional

from .enums import (
    AmmoType,
    CombatType,
    Direction,
    FloorChange,
    Fluid,
    ItemGroup,
    ItemType,
    MagicEffect,
    Race,
    ShootType,
    SlotPosition,
    WeaponType,
)


@dataclass(slots=True)
class BaseItem:
    server_id: Optional[int] = None
    client_id: Optional[int] = None
    name: Optional[str] = None
    article: Optional[str] = None
    plural: Optional[str] = None
    editor_suffix: Optional[str] = None
    sprite_hash: Optional[str] = None

    group: Optional[ItemGroup] = None
    item_type: Optional[ItemType] = None
    flags: Optional[int] = None

    allow_distance_read: bool = False
    always_on_top_order: Optional[int] = None
    ammo_type: Optional[AmmoType] = None
    armor: Optional[int] = None
    attack_speed: Optional[int] = None
    bed_partner_direction: Optional[Direction] = None
    block_projectile: bool = False
    block_solid: bool = False
    charges: Optional[int] = None
    classification: Optional[int] = None
    container_size: Optional[int] = None
    corpse_type: Optional[Race] = None
    decay_to: Optional[int] = None
    defense: Optional[int] = None
    description: Optional[str] = None
    destroy_to: Optional[int] = None
    duration: Optional[int] = None
    effect: Optional[MagicEffect] = None
    extra_defense: Optional[int] = None
    floor_change: Optional[FloorChange] = None
    fluid_source: Optional[Fluid] = None
    force_serialize: bool = False
    hit_chance: Optional[int] = None
    invisible: bool = False
    level_door: Optional[int] = None
    mana_shield: bool = False
    minimap_color: Optional[int] = None
    moveable: bool = False
    pickupable: bool = False
    range: Optional[int] = None
    replaceable: bool = False
    rotate_to: Optional[int] = None
    rune_spell_name: Optional[str] = None
    shoot_type: Optional[ShootType] = None
    show_attributes: bool = False
    show_charges: bool = False
    show_count: bool = False
    show_duration: bool = False
    speed: Optional[int] = None
    slot_type: Optional[SlotPosition] = None
    stop_duration: bool = False
    supply: bool = False
    walk_stack: bool = False
    ware_id: Optional[int] = None
    weapon_type: Optional[WeaponType] = None
    weight: Optional[int] = None
    worth: Optional[int] = None

    # weapons
    can_wield_unproperly: bool = False
    min_level: int = 0
    melee_remove_charges: bool = False
    wand_combat_type: Optional[CombatType] = None
    wand_mana: Optional[int] = None
    wand_min_damage: Optional[int] = None
    wand_max_damage: Optional[int] = None
    distance_break_chance: Optional[int] = None
    distance_remove_count: bool = False
    script: Optional[str] = None

    # transforms
    transform_deequip_to: Optional[int] = None
    transform_equip_to: Optional[int] = None
    female_transform_to_on_use: Optional[int] = None
    male_transform_to_on_use: Optional[int] = None
    transform_to_free: Optional[int] = None

    # light
    light_color: Optional[int] = None
    light_level: Optional[int] = None

    # readable & writeable
    max_text_length: Optional[int] = None
    readable: bool = False
    read_only_item_id: Optional[int] = None
    writeable: bool = False
    write_once_item_id: Optional[int] = None

    # regeneration
    health_gain: Optional[int] = None
    health_ticks: Optional[int] = None
    mana_gain: Optional[int] = None
    mana_ticks: Optional[int] = None

    # damage absorption
    absorb_percent_energy: int = 0
    absorb_percent_fire: int = 0
    absorb_percent_earth: int = 0
    absorb_percent_ice: int = 0
    absorb_percent_holy: int = 0
    absorb_percent_death: int = 0
    absorb_percent_life_drain: int = 0
    absorb_percent_mana_drain: int = 0
    absorb_percent_drown: int = 0
    absorb_percent_physical: int = 0
    absorb_percent_healing: int = 0
    absorb_percent_undefined: int = 0

    vocations: Optional[set[str]] = None

    # attack
    attack: int = 0
    element_ice: int = 0
    element_earth: int = 0
    element_fire: int = 0
    element_energy: int = 0
    element_death: int = 0
    element_holy: int = 0
    max_hit_chance: int = 100

    # field damage absorption
    field_absorb_percent_energy: int = 0
    field_absorb_percent_fire: int = 0
    field_absorb_percent_earth: int = 0

    # skill requirements
    skill_sword: Optional[int] = None
    skill_axe: Optional[int] = None
    skill_club: Optional[int] = None
    skill_dist: Optional[int] = None
    skill_fish: Optional[int] = None
    skill_shield: Optional[int] = None
    skill_fist: Optional[int] = None

    # stats
    magic_level_points: Optional[int] = None
    magic_level_points_percent: Optional[int] = None

    # suppression
    suppress_curse: bool = False
    suppress_dazzle: bool = False
    suppress_drown: bool = False
    suppress_drunk: bool = False
    suppress_energy: bool = False
    suppress_fire: bool = False
    suppress_freeze: bool = False
    suppress_physical: bool = False
    suppress_poison: bool = False


BaseItemDict = dict[int, BaseItem]
