import xml.etree.ElementTree as ET
from functools import partial, reduce
from os import PathLike
from typing import Any

from .base_item import BaseItem, BaseItemDict
from .enums import (
    AmmoType,
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

ammo_types = {
    "spear": AmmoType.SPEAR,
    "bolt": AmmoType.BOLT,
    "arrow": AmmoType.ARROW,
    "poisonarrow": AmmoType.ARROW,
    "burstarrow": AmmoType.ARROW,
    "throwingstar": AmmoType.THROWING_STAR,
    "throwingknife": AmmoType.THROWING_KNIFE,
    "smallstone": AmmoType.STONE,
    "largerock": AmmoType.STONE,
    "snowball": AmmoType.SNOW_BALL,
    "powerbolt": AmmoType.BOLT,
    "infernalbolt": AmmoType.BOLT,
    "huntingspear": AmmoType.SPEAR,
    "enchantedspear": AmmoType.SPEAR,
    "royalspear": AmmoType.SPEAR,
    "sniperarrow": AmmoType.ARROW,
    "onyxarrow": AmmoType.ARROW,
    "piercingbolt": AmmoType.BOLT,
    "etherealspear": AmmoType.SPEAR,
    "flasharrow": AmmoType.ARROW,
    "flammingarrow": AmmoType.ARROW,
    "shiverarrow": AmmoType.ARROW,
    "eartharrow": AmmoType.ARROW,
    "tarsalarrow": AmmoType.ARROW,
    "vortexbolt": AmmoType.BOLT,
    "prismaticbolt": AmmoType.BOLT,
    "crystallinearrow": AmmoType.ARROW,
    "drillbolt": AmmoType.BOLT,
    "envenomedarrow": AmmoType.ARROW,
    "gloothspear": AmmoType.SPEAR,
    "simplearrow": AmmoType.ARROW,
    "redstar": AmmoType.THROWING_STAR,
    "greenstar": AmmoType.THROWING_STAR,
    "leafstar": AmmoType.THROWING_STAR,
    "diamondarrow": AmmoType.ARROW,
    "spectralbolt": AmmoType.BOLT,
    "royalstar": AmmoType.THROWING_STAR,
}

directions = {
    "north": Direction.NORTH,
    "n": Direction.NORTH,
    "0": Direction.NORTH,
    "east": Direction.EAST,
    "e": Direction.EAST,
    "1": Direction.EAST,
    "south": Direction.SOUTH,
    "s": Direction.SOUTH,
    "2": Direction.SOUTH,
    "west": Direction.WEST,
    "w": Direction.WEST,
    "3": Direction.WEST,
    "southwest": Direction.SOUTH_WEST,
    "south west": Direction.SOUTH_WEST,
    "south-west": Direction.SOUTH_WEST,
    "sw": Direction.SOUTH_WEST,
    "4": Direction.SOUTH_WEST,
    "southeast": Direction.SOUTH_EAST,
    "south east": Direction.SOUTH_EAST,
    "south-east": Direction.SOUTH_EAST,
    "se": Direction.SOUTH_EAST,
    "5": Direction.SOUTH_EAST,
    "northwest": Direction.NORTH_WEST,
    "north west": Direction.NORTH_WEST,
    "north-west": Direction.NORTH_WEST,
    "nw": Direction.NORTH_WEST,
    "6": Direction.NORTH_WEST,
    "northeast": Direction.NORTH_EAST,
    "north east": Direction.NORTH_EAST,
    "north-east": Direction.NORTH_EAST,
    "ne": Direction.NORTH_EAST,
    "7": Direction.NORTH_EAST,
}

floor_changes = {
    "down": FloorChange.DOWN,
    "north": FloorChange.NORTH,
    "south": FloorChange.SOUTH,
    "southalt": FloorChange.SOUTH_ALT,
    "west": FloorChange.WEST,
    "east": FloorChange.EAST,
    "eastalt": FloorChange.EAST_ALT,
}

fluid_sources = {
    "water": Fluid.WATER,
    "blood": Fluid.BLOOD,
    "beer": Fluid.BEER,
    "slime": Fluid.SLIME,
    "lemonade": Fluid.LEMONADE,
    "milk": Fluid.MILK,
    "mana": Fluid.MANA,
    "life": Fluid.LIFE,
    "oil": Fluid.OIL,
    "urine": Fluid.URINE,
    "coconut": Fluid.COCONUT_MILK,
    "wine": Fluid.WINE,
    "mud": Fluid.MUD,
    "fruitjuice": Fluid.FRUIT_JUICE,
    "lava": Fluid.LAVA,
    "rum": Fluid.RUM,
    "swamp": Fluid.SWAMP,
    "tea": Fluid.TEA,
    "mead": Fluid.MEAD,
    "ink": Fluid.INK,
}

item_types = {
    "key": ItemType.KEY,
    "magicfield": ItemType.MAGIC_FIELD,
    "container": ItemType.CONTAINER,
    "depot": ItemType.DEPOT,
    "mailbox": ItemType.MAILBOX,
    "trashholder": ItemType.TRASH_HOLDER,
    "teleport": ItemType.TELEPORT,
    "door": ItemType.DOOR,
    "bed": ItemType.BED,
    "rune": ItemType.RUNE,
    "podium": ItemType.PODIUM,
}

magic_effects = {
    "redspark": MagicEffect.DRAW_BLOOD,
    "bluebubble": MagicEffect.LOSE_ENERGY,
    "poff": MagicEffect.POFF,
    "yellowspark": MagicEffect.BLOCK_HIT,
    "explosionarea": MagicEffect.EXPLOSION_AREA,
    "explosion": MagicEffect.EXPLOSION_HIT,
    "firearea": MagicEffect.FIRE_AREA,
    "yellowbubble": MagicEffect.YELLOW_RINGS,
    "greenbubble": MagicEffect.GREEN_RINGS,
    "blackspark": MagicEffect.HIT_AREA,
    "teleport": MagicEffect.TELEPORT,
    "energy": MagicEffect.ENERGY_HIT,
    "blueshimmer": MagicEffect.MAGIC_BLUE,
    "redshimmer": MagicEffect.MAGIC_RED,
    "greenshimmer": MagicEffect.MAGIC_GREEN,
    "fire": MagicEffect.HIT_BY_FIRE,
    "greenspark": MagicEffect.HIT_BY_POISON,
    "mortarea": MagicEffect.MORT_AREA,
    "greennote": MagicEffect.SOUND_GREEN,
    "rednote": MagicEffect.SOUND_RED,
    "poison": MagicEffect.POISON_AREA,
    "yellownote": MagicEffect.SOUND_YELLOW,
    "purplenote": MagicEffect.SOUND_PURPLE,
    "bluenote": MagicEffect.SOUND_BLUE,
    "whitenote": MagicEffect.SOUND_WHITE,
    "bubbles": MagicEffect.BUBBLES,
    "dice": MagicEffect.CRAPS,
    "giftwraps": MagicEffect.GIFT_WRAPS,
    "yellowfirework": MagicEffect.FIREWORK_YELLOW,
    "redfirework": MagicEffect.FIREWORK_RED,
    "bluefirework": MagicEffect.FIREWORK_BLUE,
    "stun": MagicEffect.STUN,
    "sleep": MagicEffect.SLEEP,
    "watercreature": MagicEffect.WATER_CREATURE,
    "groundshaker": MagicEffect.GROUNDSHAKER,
    "hearts": MagicEffect.HEARTS,
    "fireattack": MagicEffect.FIRE_ATTACK,
    "energyarea": MagicEffect.ENERGY_AREA,
    "smallclouds": MagicEffect.SMALL_CLOUDS,
    "holydamage": MagicEffect.HOLY_DAMAGE,
    "bigclouds": MagicEffect.BIG_CLOUDS,
    "icearea": MagicEffect.ICE_AREA,
    "icetornado": MagicEffect.ICE_TORNADO,
    "iceattack": MagicEffect.ICE_ATTACK,
    "stones": MagicEffect.STONES,
    "smallplants": MagicEffect.SMALL_PLANTS,
    "carniphila": MagicEffect.CARNIPHILA,
    "purpleenergy": MagicEffect.PURPLE_ENERGY,
    "yellowenergy": MagicEffect.YELLOW_ENERGY,
    "holyarea": MagicEffect.HOLY_AREA,
    "bigplants": MagicEffect.BIG_PLANTS,
    "cake": MagicEffect.CAKE,
    "giantice": MagicEffect.GIANTICE,
    "watersplash": MagicEffect.WATERSPLASH,
    "plantattack": MagicEffect.PLANTATTACK,
    "tutorialarrow": MagicEffect.TUTORIALARROW,
    "tutorialsquare": MagicEffect.TUTORIALSQUARE,
    "mirrorhorizontal": MagicEffect.MIRRORHORIZONTAL,
    "mirrorvertical": MagicEffect.MIRRORVERTICAL,
    "skullhorizontal": MagicEffect.SKULLHORIZONTAL,
    "skullvertical": MagicEffect.SKULLVERTICAL,
    "assassin": MagicEffect.ASSASSIN,
    "stepshorizontal": MagicEffect.STEPSHORIZONTAL,
    "bloodysteps": MagicEffect.BLOODYSTEPS,
    "stepsvertical": MagicEffect.STEPSVERTICAL,
    "yalaharighost": MagicEffect.YALAHARIGHOST,
    "bats": MagicEffect.BATS,
    "smoke": MagicEffect.SMOKE,
    "insects": MagicEffect.INSECTS,
    "dragonhead": MagicEffect.DRAGONHEAD,
    "orcshaman": MagicEffect.ORCSHAMAN,
    "orcshamanfire": MagicEffect.ORCSHAMAN_FIRE,
    "thunder": MagicEffect.THUNDER,
    "ferumbras": MagicEffect.FERUMBRAS,
    "confettihorizontal": MagicEffect.CONFETTI_HORIZONTAL,
    "confettivertical": MagicEffect.CONFETTI_VERTICAL,
    "blacksmoke": MagicEffect.BLACKSMOKE,
    "redsmoke": MagicEffect.REDSMOKE,
    "yellowsmoke": MagicEffect.YELLOWSMOKE,
    "greensmoke": MagicEffect.GREENSMOKE,
    "purplesmoke": MagicEffect.PURPLESMOKE,
    "earlythunder": MagicEffect.EARLY_THUNDER,
    "bonecapsule": MagicEffect.RAGIAZ_BONECAPSULE,
    "criticaldamage": MagicEffect.CRITICAL_DAMAGE,
    "plungingfish": MagicEffect.PLUNGING_FISH,
    "bluechain": MagicEffect.BLUECHAIN,
    "orangechain": MagicEffect.ORANGECHAIN,
    "greenchain": MagicEffect.GREENCHAIN,
    "purplechain": MagicEffect.PURPLECHAIN,
    "greychain": MagicEffect.GREYCHAIN,
    "yellowchain": MagicEffect.YELLOWCHAIN,
    "yellowsparkles": MagicEffect.YELLOWSPARKLES,
    "faeexplosion": MagicEffect.FAEEXPLOSION,
    "faecoming": MagicEffect.FAECOMING,
    "faegoing": MagicEffect.FAEGOING,
    "bigcloudssinglespace": MagicEffect.BIGCLOUDSSINGLESPACE,
    "stonessinglespace": MagicEffect.STONESSINGLESPACE,
    "blueghost": MagicEffect.BLUEGHOST,
    "pointofinterest": MagicEffect.POINTOFINTEREST,
    "mapeffect": MagicEffect.MAPEFFECT,
    "pinkspark": MagicEffect.PINKSPARK,
    "greenfirework": MagicEffect.FIREWORK_GREEN,
    "orangefirework": MagicEffect.FIREWORK_ORANGE,
    "purplefirework": MagicEffect.FIREWORK_PURPLE,
    "turquoisefirework": MagicEffect.FIREWORK_TURQUOISE,
    "thecube": MagicEffect.THECUBE,
    "drawink": MagicEffect.DRAWINK,
    "prismaticsparkles": MagicEffect.PRISMATICSPARKLES,
    "thaian": MagicEffect.THAIAN,
    "thaianghost": MagicEffect.THAIANGHOST,
    "ghostsmoke": MagicEffect.GHOSTSMOKE,
    "floatingblock": MagicEffect.FLOATINGBLOCK,
    "block": MagicEffect.BLOCK,
    "rooting": MagicEffect.ROOTING,
    "ghostlyscratch": MagicEffect.GHOSTLYSCRATCH,
    "ghostlybite": MagicEffect.GHOSTLYBITE,
    "bigscratching": MagicEffect.BIGSCRATCHING,
    "slash": MagicEffect.SLASH,
    "bite": MagicEffect.BITE,
    "chivalriouschallenge": MagicEffect.CHIVALRIOUSCHALLENGE,
    "divinedazzle": MagicEffect.DIVINEDAZZLE,
    "electricalspark": MagicEffect.ELECTRICALSPARK,
    "purpleteleport": MagicEffect.PURPLETELEPORT,
    "redteleport": MagicEffect.REDTELEPORT,
    "orangeteleport": MagicEffect.ORANGETELEPORT,
    "greyteleport": MagicEffect.GREYTELEPORT,
    "lightblueteleport": MagicEffect.LIGHTBLUETELEPORT,
    "fatal": MagicEffect.FATAL,
    "dodge": MagicEffect.DODGE,
    "hourglass": MagicEffect.HOURGLASS,
    "ferumbras1": MagicEffect.FERUMBRAS_1,
    "gazharagoth": MagicEffect.GAZHARAGOTH,
    "madmage": MagicEffect.MAD_MAGE,
    "horestis": MagicEffect.HORESTIS,
    "devovorga": MagicEffect.DEVOVORGA,
    "ferumbras2": MagicEffect.FERUMBRAS_2,
}

races = {
    "venom": Race.VENOM,
    "blood": Race.BLOOD,
    "undead": Race.UNDEAD,
    "fire": Race.FIRE,
    "energy": Race.ENERGY,
    "ink": Race.INK,
}

shoot_types = {
    "spear": ShootType.SPEAR,
    "bolt": ShootType.BOLT,
    "arrow": ShootType.ARROW,
    "fire": ShootType.FIRE,
    "energy": ShootType.ENERGY,
    "poisonarrow": ShootType.POISONARROW,
    "burstarrow": ShootType.BURSTARROW,
    "throwingstar": ShootType.THROWINGSTAR,
    "throwingknife": ShootType.THROWINGKNIFE,
    "smallstone": ShootType.SMALLSTONE,
    "death": ShootType.DEATH,
    "largerock": ShootType.LARGEROCK,
    "snowball": ShootType.SNOWBALL,
    "powerbolt": ShootType.POWERBOLT,
    "poison": ShootType.POISON,
    "infernalbolt": ShootType.INFERNALBOLT,
    "huntingspear": ShootType.HUNTINGSPEAR,
    "enchantedspear": ShootType.ENCHANTEDSPEAR,
    "redstar": ShootType.REDSTAR,
    "greenstar": ShootType.GREENSTAR,
    "royalspear": ShootType.ROYALSPEAR,
    "sniperarrow": ShootType.SNIPERARROW,
    "onyxarrow": ShootType.ONYXARROW,
    "piercingbolt": ShootType.PIERCINGBOLT,
    "whirlwindsword": ShootType.WHIRLWINDSWORD,
    "whirlwindaxe": ShootType.WHIRLWINDAXE,
    "whirlwindclub": ShootType.WHIRLWINDCLUB,
    "etherealspear": ShootType.ETHEREALSPEAR,
    "ice": ShootType.ICE,
    "earth": ShootType.EARTH,
    "holy": ShootType.HOLY,
    "suddendeath": ShootType.SUDDENDEATH,
    "flasharrow": ShootType.FLASHARROW,
    "flammingarrow": ShootType.FLAMMINGARROW,
    "shiverarrow": ShootType.SHIVERARROW,
    "energyball": ShootType.ENERGYBALL,
    "smallice": ShootType.SMALLICE,
    "smallholy": ShootType.SMALLHOLY,
    "smallearth": ShootType.SMALLEARTH,
    "eartharrow": ShootType.EARTHARROW,
    "explosion": ShootType.EXPLOSION,
    "cake": ShootType.CAKE,
    "tarsalarrow": ShootType.TARSALARROW,
    "vortexbolt": ShootType.VORTEXBOLT,
    "prismaticbolt": ShootType.PRISMATICBOLT,
    "crystallinearrow": ShootType.CRYSTALLINEARROW,
    "drillbolt": ShootType.DRILLBOLT,
    "envenomedarrow": ShootType.ENVENOMEDARROW,
    "gloothspear": ShootType.GLOOTHSPEAR,
    "simplearrow": ShootType.SIMPLEARROW,
    "leafstar": ShootType.LEAFSTAR,
    "diamondarrow": ShootType.DIAMONDARROW,
    "spectralbolt": ShootType.SPECTRALBOLT,
    "royalstar": ShootType.ROYALSTAR,
}

slot_types = {
    "head": SlotPosition.HEAD,
    "body": SlotPosition.ARMOR,
    "legs": SlotPosition.LEGS,
    "feet": SlotPosition.FEET,
    "backpack": SlotPosition.BACKPACK,
    "two-handed": SlotPosition.TWO_HAND,
    "right-hand": SlotPosition.LEFT,
    "left-hand": SlotPosition.RIGHT,
    "necklace": SlotPosition.NECKLACE,
    "ring": SlotPosition.RING,
    "ammo": SlotPosition.AMMO,
    "hand": SlotPosition.HAND,
}

weapon_types = {
    "sword": WeaponType.SWORD,
    "club": WeaponType.CLUB,
    "axe": WeaponType.AXE,
    "shield": WeaponType.SHIELD,
    "distance": WeaponType.DISTANCE,
    "wand": WeaponType.WAND,
    "ammunition": WeaponType.AMMO,
    "quiver": WeaponType.QUIVER,
}

combat_types = {
    "all": [
        "energy",
        "fire",
        "earth",
        "ice",
        "holy",
        "death",
        "life_drain",
        "mana_drain",
        "drown",
        "physical",
        "healing",
        "undefined",
    ],
    "elements": ["energy", "fire", "earth", "ice"],
    "magic": ["energy", "fire", "earth", "ice", "holy", "death"],
}

mapped_props: dict[str, dict[str, Any]] = {
    "ammo_type": ammo_types,
    "bed_partner_direction": directions,
    "corpse_type": races,
    "effect": magic_effects,
    "fluid_source": fluid_sources,
    "item_type": item_types,
    "shoot_type": shoot_types,
    "weapon_type": weapon_types,
}

renamed_props = {
    "absorbpercentall": "absorb_percent_all",
    "absorbpercentallelements": "absorb_percent_all",
    "absorbpercentdeath": "absorb_percent_death",
    "absorbpercentdrown": "absorb_percent_drown",
    "absorbpercentearth": "absorb_percent_earth",
    "absorbpercentelements": "absorb_percent_elements",
    "absorbpercentenergy": "absorb_percent_energy",
    "absorbpercentfire": "absorb_percent_fire",
    "absorbpercenthealing": "absorb_percent_healing",
    "absorbpercentholy": "absorb_percent_holy",
    "absorbpercentice": "absorb_percent_ice",
    "absorbpercentlifedrain": "absorb_percent_life_drain",
    "absorbpercentmagic": "absorb_percent_magic",
    "absorbpercentmanadrain": "absorb_percent_mana_drain",
    "absorbpercentphysical": "absorb_percent_physical",
    "absorbpercentpoison": "absorb_percent_earth",
    "absorbpercentundefined": "absorb_percent_undefined",
    "ammotype": "ammo_type",
    "allowdistread": "allow_distance_read",
    "allowpickupable": "pickupable",
    "blockprojectile": "block_projectile",
    "blocking": "block_solid",
    "containersize": "container_size",
    "corpsetype": "corpse_type",
    "decayto": "decay_to",
    "destroyto": "destroy_to",
    "elementdeath": "element_death",
    "elementearth": "element_earth",
    "elementenergy": "element_energy",
    "elementfire": "element_fire",
    "elementholy": "element_holy",
    "elementice": "element_ice",
    "extradef": "extra_defense",
    "femalesleeper": "female_transform_to_on_use",
    "femaletransformto": "female_transform_to_on_use",
    "fieldabsorbpercentenergy": "field_absorb_percent_energy",
    "fieldabsorbpercentfire": "field_absorb_percent_fire",
    "fieldabsorbpercentpoison": "field_absorb_percent_earth",
    "fieldabsorbpercentearth": "field_absorb_percent_earth",
    "floorchange": "floor_change",
    "fluidsource": "fluid_source",
    "forceserialize": "force_serialize",
    "healthgain": "health_gain",
    "healthticks": "health_ticks",
    "hitchance": "hit_chance",
    "leveldoor": "level_door",
    "magiclevelpoints": "magic_level_points",
    "magiclevelpointspercent": "magic_level_points_percent",
    "malesleeper": "male_transform_to_on_use",
    "maletransformto": "male_transform_to_on_use",
    "managain": "mana_gain",
    "manashield": "mana_shield",
    "manaticks": "mana_ticks",
    "maxhitchance": "max_hit_chance",
    "maxtextlen": "max_text_length",
    "partnerdirection": "bed_partner_direction",
    "rotateto": "rotate_to",
    "runespellname": "rune_spell_name",
    "shoottype": "shoot_type",
    "showattributes": "show_attributes",
    "showcharges": "show_charges",
    "showcount": "show_count",
    "showduration": "show_duration",
    "skillaxe": "skill_axe",
    "skillclub": "skill_club",
    "skilldist": "skill_dist",
    "skillfish": "skill_fish",
    "skillfist": "skill_fist",
    "skillshield": "skill_shield",
    "skillsword": "skill_sword",
    "slottype": "slot_type",
    "stopduration": "stop_duration",
    "suppresscurse": "suppress_curse",
    "suppressdazzle": "suppress_dazzle",
    "suppressdrown": "suppress_drown",
    "suppressdrunk": "suppress_drunk",
    "suppressenergy": "suppress_energy",
    "suppressfire": "suppress_fire",
    "suppressfreeze": "suppress_freeze",
    "suppressphysical": "suppress_physical",
    "suppresspoison": "suppress_poison",
    "transformdeequipto": "transform_deequip_to",
    "transformequipto": "transform_equip_to",
    "type": "item_type",
    "walkstack": "walk_stack",
    "weapontype": "weapon_type",
    "writeonceitemid": "write_once_item_id",
}


def set_abilities(item: BaseItem, ability: str, key: str, value: int):
    """
    >>> item = BaseItem()
    >>> set_abilities(item, "absorb_percent", "absorb_percent_energy", 10)
    >>> item.absorb_percent_energy
    10
    >>> set_abilities(item, "absorb_percent", "absorb_percent_elements", 10)
    >>> item.absorb_percent_energy, item.absorb_percent_fire, item.absorb_percent_earth, item.absorb_percent_ice
    (20, 10, 10, 10)
    """
    prefix_len = len(ability) + 1
    combat_type = key[prefix_len:]

    for damage_type in combat_types.get(combat_type, [combat_type]):
        current: int = getattr(item, f"{ability}_{damage_type}")
        assert isinstance(current, int)
        setattr(item, f"{ability}_{damage_type}", current + value)


def parse_item_ids(element: ET.Element):
    """
    >>> element = ET.fromstring('<item id="100"/>')
    >>> [*parse_item_ids(element)]
    [100]
    >>> element = ET.fromstring('<item fromid="101" toid="104"/>')
    >>> [*parse_item_ids(element)]
    [101, 102, 103, 104]
    """
    if id_ := element.get("id"):
        yield int(id_)
        return

    from_id, to_id = element.get("fromid"), element.get("toid")
    if from_id and to_id:
        yield from range(int(from_id), int(to_id) + 1)


def parse_attributes(
    element: ET.Element, items: BaseItemDict, item_id: int
) -> BaseItemDict:
    """Parse attributes of a element."""
    item = items.get(item_id)
    if not item:
        item = BaseItem(server_id=item_id)

    item.name = element.get("name")
    item.article = element.get("article")
    item.plural = element.get("plural")
    item.editor_suffix = element.get("editor_suffix")

    for child in element:
        assert child.tag == "attribute", f"Tag should be 'attribute', found {child.tag}"

        key = child.get("key", "").lower()
        assert key

        value = child.get("value")
        assert value

        match k := renamed_props.get(key, key):
            case "allow_distance_read" | "block_projectile" | "block_solid" | "force_serialize" | "invisible" | "mana_shield" | "moveable" | "pickupable" | "readable" | "replaceable" | "show_attributes" | "show_charges" | "show_count" | "show_duration" | "stop_duration" | "supply" | "suppress_curse" | "suppress_dazzle" | "suppress_drown" | "suppress_drunk" | "suppress_energy" | "suppress_fire" | "suppress_freeze" | "suppress_physical" | "suppress_poison" | "walk_stack" | "writeable":
                setattr(item, k, value[0] in "1tTyY")

            case "armor" | "attack" | "charges" | "container_size" | "decay_to" | "defense" | "destroy_to" | "duration" | "extra_defense" | "health_gain" | "health_ticks" | "hit_chance" | "level_door" | "magic_level_points" | "magic_level_points_percent" | "mana_gain" | "mana_ticks" | "max_hit_chance" | "max_text_length" | "range" | "rotate_to" | "skill_axe" | "skill_club" | "skill_dist" | "skill_fish" | "skill_fist" | "skill_shield" | "skill_sword" | "speed" | "transform_deequip_to" | "transform_equip_to" | "worth":
                setattr(item, k, int(value))

            case "ammo_type" | "bed_partner_direction" | "corpse_type" | "effect" | "fluid_source" | "item_type" | "shoot_type" | "weapon_type":
                values = mapped_props[k]
                setattr(item, k, values[value.lower()])

            case "absorb_percent_all" | "absorb_percent_elements" | "absorb_percent_magic" | "absorb_percent_death" | "absorb_percent_drown" | "absorb_percent_earth" | "absorb_percent_energy" | "absorb_percent_fire" | "absorb_percent_healing" | "absorb_percent_holy" | "absorb_percent_ice" | "absorb_percent_life_drain" | "absorb_percent_mana_drain" | "absorb_percent_physical" | "absorb_percent_earth" | "absorb_percent_undefined":
                set_abilities(item, "absorb_percent", k, int(value))

            case "element_death" | "element_earth" | "element_energy" | "element_fire" | "element_holy" | "element_ice":
                set_abilities(item, "element", k, int(value))

            case "field_absorb_percent_energy" | "field_absorb_percent_fire" | "field_absorb_percent_earth":
                set_abilities(item, "field_absorb_percent", k, int(value))

            case "field":
                item.group = ItemGroup.MAGIC_FIELD
                item.item_type = ItemType.MAGIC_FIELD

                # TODO: combat type

            case "floor_change":
                current_floor_change = item.floor_change or FloorChange(0)
                item.floor_change = current_floor_change | floor_changes[value.lower()]

            case "female_transform_to_on_use" | "male_transform_to_on_use":
                v = int(value)
                setattr(item, k, v)

                other = items[v]
                if not other.transform_to_free:
                    other.transform_to_free = item_id

                setattr(item, k, item_id)
                # transform_to_on_use.setdefault(PlayerSex.FEMALE, v)

            case "slot_type":
                current_slot_type = item.slot_type or SlotPosition.HAND

                match slot_type := slot_types[value.lower()]:
                    case "right-hand":
                        item.slot_type = current_slot_type & ~SlotPosition.LEFT

                    case "left-hand":
                        item.slot_type = current_slot_type & ~SlotPosition.RIGHT

                    case _:
                        item.slot_type = current_slot_type | slot_type

            case "weight":
                item.weight = int(value)

            case "description" | "rune_spell_name" | "write_once_item_id":
                setattr(item, k, value)

            # case _:
            #     raise NotImplementedError(f"Unknown key {k}")

    if not item.client_id:
        print(f"[Warning] Item {item_id} has no client id")

    items[item_id] = item
    return items


def parse_item_tag(items: BaseItemDict, element: ET.Element) -> BaseItemDict:
    assert element.tag == "item", f"Tag should be 'item', found {element.tag}"

    return reduce(partial(parse_attributes, element), parse_item_ids(element), items)


def load_items_xml(path: PathLike, items: BaseItemDict) -> BaseItemDict:
    tree = ET.parse(path)

    root = tree.getroot()
    assert root.tag == "items"

    return reduce(parse_item_tag, root, items)
