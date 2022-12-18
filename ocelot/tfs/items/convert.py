from ocelot.items.weapon import Wand

from ...items.ammunition import Ammunition, AmmunitionType
from ...items.ammunition import ShootType as AmmoShootType
from .base_item import BaseItem
from .enums import AmmoType, ItemGroup, ShootType, WeaponType

ammo_types = {AmmoType.ARROW: AmmunitionType.ARROW, AmmoType.BOLT: AmmunitionType.BOLT}

shoot_types = {
    ShootType.BOLT: AmmoShootType.BOLT,
    ShootType.ARROW: AmmoShootType.ARROW,
    ShootType.POISONARROW: AmmoShootType.POISON_ARROW,
    ShootType.BURSTARROW: AmmoShootType.BURST_ARROW,
    ShootType.POWERBOLT: AmmoShootType.POWER_BOLT,
    ShootType.INFERNALBOLT: AmmoShootType.INFERNAL_BOLT,
    ShootType.SNIPERARROW: AmmoShootType.SNIPER_ARROW,
    ShootType.ONYXARROW: AmmoShootType.ONYX_ARROW,
    ShootType.PIERCINGBOLT: AmmoShootType.PIERCING_BOLT,
    ShootType.FLASHARROW: AmmoShootType.FLASH_ARROW,
    ShootType.FLAMMINGARROW: AmmoShootType.FLAMMING_ARROW,
    ShootType.SHIVERARROW: AmmoShootType.SHIVER_ARROW,
    ShootType.EARTHARROW: AmmoShootType.EARTH_ARROW,
    ShootType.TARSALARROW: AmmoShootType.TARSAL_ARROW,
    ShootType.VORTEXBOLT: AmmoShootType.VORTEX_BOLT,
    ShootType.PRISMATICBOLT: AmmoShootType.PRISMATIC_BOLT,
    ShootType.CRYSTALLINEARROW: AmmoShootType.CRYSTALLINE_ARROW,
    ShootType.DRILLBOLT: AmmoShootType.DRILL_BOLT,
    ShootType.ENVENOMEDARROW: AmmoShootType.ENVENOMED_ARROW,
    ShootType.SIMPLEARROW: AmmoShootType.SIMPLE_ARROW,
    ShootType.DIAMONDARROW: AmmoShootType.DIAMOND_ARROW,
    ShootType.SPECTRALBOLT: AmmoShootType.SPECTRAL_BOLT,
}


def convert_item(item: BaseItem):
    assert item.server_id

    if item.group == ItemGroup.GROUND:
        pass

    if item.weapon_type == WeaponType.AMMO:
        assert item.name
        assert item.ammo_type in ammo_types
        assert item.shoot_type in shoot_types
        assert item.weight is not None
        assert item.vocations is not None
        assert item.distance_remove_count

        return Ammunition(
            id=item.server_id,
            name=item.name,
            article=item.article,
            plural=item.plural,
            editor_suffix=item.editor_suffix,
            sprite_hash=item.sprite_hash,
            ammo_type=ammo_types[item.ammo_type],
            shoot_type=shoot_types[item.shoot_type],
            vocations=item.vocations,
            weight=item.weight,
            attack_physical=item.attack,
            attack_earth=item.element_earth,
            attack_energy=item.element_energy,
            attack_fire=item.element_fire,
            attack_ice=item.element_ice,
            max_hit_chance=item.max_hit_chance,
            min_level=item.min_level,
        )

    if item.weapon_type == WeaponType.WAND:
        assert item.name
        assert item.weight is not None
        # assert isinstance(item.vocations, set)
        assert item.range
        assert item.wand_mana
        assert item.wand_max_damage
        assert item.wand_min_damage

        return Wand(
            id=item.server_id,
            name=item.name,
            article=item.article,
            plural=item.plural,
            editor_suffix=item.editor_suffix,
            sprite_hash=item.sprite_hash,
            vocations=item.vocations,
            weight=item.weight,
            light_color=item.light_color,
            light_level=item.light_level,
            min_level=item.min_level,
            range=item.range,
            mana_cost=item.wand_mana,
            max_damage=item.wand_max_damage,
            min_damage=item.wand_min_damage,
        )

    return item
    # else:
    #     raise NotImplementedError(f"Unknown weapon type: {item.weapon_type}")
