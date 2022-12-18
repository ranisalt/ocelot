import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from os import PathLike, path
from typing import Generator

MAX_LOOT_CHANCE = 100_000


@dataclass(slots=True)
class Summon:
    name: str
    interval: int
    chance: int


@dataclass(slots=True)
class Attack:
    name: str
    interval: int
    chance: int
    min: int
    max: int
    range: int
    # needs_target: bool

    area_effect: str = ""


@dataclass(slots=True)
class Voice:
    sentence: str
    yell: bool


@dataclass(slots=True)
class Loot:
    id: int
    name: str
    chance: int
    max_count: int


@dataclass(slots=True)
class Monster:
    name: str
    description: str
    experience: int
    speed: int

    health: int = 0
    max_health: int = 0
    run_away_health: int = 0

    look_corpse: int = 0
    look_type: int = 0
    look_type_ex: int = 0
    look_head: int = 0
    look_body: int = 0
    look_legs: int = 0
    look_feet: int = 0
    look_addons: int = 0
    look_mount: int = 0

    target_change_interval: int = 0
    target_change_chance: int = 0
    target_distance: int = 0

    static_attack: int = 0

    armor: int = 0
    defense: int = 0

    attackable: bool = False
    can_push_creatures: bool = False
    can_push_items: bool = False
    can_walk_on_energy: bool = False
    can_walk_on_fire: bool = False
    can_walk_on_poison: bool = False
    convinceable: bool = False
    hide_health: bool = False
    hostile: bool = False
    ignore_spawn_block: bool = False
    illusionable: bool = False
    is_boss: bool = False
    pushable: bool = False
    summonable: bool = False

    immunity_death: bool = False
    immunity_drowning: bool = False
    immunity_drunkness: bool = False
    immunity_earth: bool = False
    immunity_energy: bool = False
    immunity_fire: bool = False
    immunity_holy: bool = False
    immunity_ice: bool = False
    immunity_invisibility: bool = False
    immunity_life_drain: bool = False
    immunity_mana_drain: bool = False
    immunity_outfit: bool = False  # what the fuck is this
    immunity_paralysis: bool = False
    immunity_physical: bool = False

    damage_taken_death: int = 100
    damage_taken_drowning: int = 100
    damage_taken_earth: int = 100
    damage_taken_energy: int = 100
    damage_taken_fire: int = 100
    damage_taken_holy: int = 100
    damage_taken_ice: int = 100
    damage_taken_life_drain: int = 100
    damage_taken_physical: int = 100

    # immunity_freeze: bool = False
    # immunity_dazzle: bool = False
    # immunity_curse: bool = False
    # immunity_bleed: bool = False

    max_summons: int = 0
    summons: tuple[Summon] = field(default_factory=tuple)

    voice_interval: int = 0
    voice_chance: int = 0
    voices: tuple[Voice] = field(default_factory=tuple)

    loot: tuple[Loot] = field(default_factory=tuple)


renamed_looktype = {
    "typeex": "type_ex",
}

renamed_flags = {
    "canpushcreatures": "can_push_creatures",
    "canpushitems": "can_push_items",
    "canwalkonenergy": "can_walk_on_energy",
    "canwalkonfire": "can_walk_on_fire",
    "canwalkonpoison": "can_walk_on_poison",
    "hidehealth": "hide_health",
    "ignorespawnblock": "ignore_spawn_block",
    "isboss": "is_boss",
    "runonhealth": "run_away_health",
    "staticattack": "static_attack",
    "targetdistance": "target_distance",
}

renamed_elements = {
    "drown": "drowning",
    "drunk": "drunkness",
    "invisible": "invisibility",
    "lifedrain": "life_drain",
    "manadrain": "mana_drain",
    "paralyze": "paralysis",
    "poison": "earth",
}


def load_monster(path: PathLike) -> Monster:
    tree = ET.parse(path)

    root = tree.getroot()
    assert root.tag == "monster"

    name = root.get("name")
    description = root.get("nameDescription")
    # race = root.get("race")  # unused
    experience = int(root.get("experience", "0"))
    speed = int(root.get("speed"))

    monster = Monster(name, description, experience, speed)

    for child in root:
        match child.tag:
            case "health":
                monster.health = int(child.get("now"))
                monster.max_health = int(child.get("max"))

            case "look":
                for key, value in child.attrib.items():
                    match k := renamed_looktype.get(key, key):
                        case "addons" | "body" | "corpse" | "feet" | "head" | "mount" | "legs" | "type" | "type_ex":
                            setattr(monster, f"look_{k}", int(value))

                        case _:
                            raise ValueError(f"Unknown look attribute: {key}")

            case "targetchange":
                interval = int(child.get("interval", child.get("speed")))
                monster.target_change_interval = interval
                monster.target_change_chance = int(child.get("chance"))

            case "flags":
                for flag in child:
                    assert flag.tag == "flag"

                    for key, value in flag.attrib.items():
                        match k := renamed_flags.get(key, key):
                            case "attackable" | "can_push_creatures" | "can_push_items" | "can_walk_on_energy" | "can_walk_on_fire" | "can_walk_on_poison" | "convinceable" | "hide_health" | "hostile" | "ignore_spawn_block" | "illusionable" | "is_boss" | "pushable" | "summonable":
                                setattr(monster, k, value[0] in "1tTyY")

                            case "run_away_health" | "static_attack" | "target_distance":
                                setattr(monster, k, int(value))

                            case _:
                                raise ValueError(f"Invalid flag: {k}")

            case "attacks":
                for attack in child:
                    assert attack.tag == "attack"

                    name = attack.get("name")
                    interval = int(attack.get("interval", attack.get("speed", "2000")))
                    chance = int(attack.get("chance", "100"))
                    min_value = int(attack.get("min", "0"))
                    max_value = int(attack.get("max", "0"))
                    range = int(attack.get("range", "0"))
                    # needs_target = attack.get("target", "0")[0] in "1tTyY"

                    # attributes = {}
                    # for attribute in attack:
                    #     assert attribute.tag == "attribute"

                    attack = Attack(
                        name,
                        interval,
                        chance,
                        min_value,
                        max_value,
                        range,
                        # needs_target,
                        # **attributes,
                    )

            case "defenses":
                monster.armor = int(child.get("armor", "0"))
                monster.defense = int(child.get("defense", "0"))

                for defense in child:
                    assert defense.tag == "defense"

                    for attribute in defense:
                        assert attribute.tag == "attribute"

            case "elements":
                for element in child:
                    assert element.tag == "element"

                    for key, value in element.attrib.items():
                        assert key.endswith("Percent"), key

                        key = key.removesuffix("Percent")
                        match k := renamed_elements.get(key, key):
                            case "death" | "drowning" | "earth" | "energy" | "fire" | "holy" | "ice" | "life_drain" | "physical":
                                setattr(monster, f"damage_taken_{k}", 100 - int(value))

                            case _:
                                raise ValueError(f"Invalid element: {k}")

            case "immunities":
                for immunity in child:
                    assert immunity.tag == "immunity"

                    for key, value in immunity.attrib.items():
                        match k := renamed_elements.get(key, key):
                            case "death" | "drowning" | "drunkness" | "earth" | "energy" | "fire" | "holy" | "ice" | "invisibility" | "life_drain" | "mana_drain" | "outfit" | "paralysis" | "physical":
                                setattr(monster, f"immunity_{k}", value[0] in "1tTyY")

                            case _:
                                raise ValueError(f"Unknown immunity attribute: {key}")

            case "summons":
                monster.max_summons = int(child.get("maxSummons"))

                summons = []
                for summon in child:
                    assert summon.tag == "summon"

                    name = summon.get("name")
                    interval = int(summon.get("interval", summon.get("speed")))
                    chance = int(summon.get("chance"))

                    summons.append(Summon(name, interval, chance))

                monster.summons = tuple(summons)

            case "voices":
                interval = int(child.get("interval", child.get("speed", "0")))
                monster.voice_interval = interval
                monster.voice_chance = min(100, int(child.get("chance", "100")))

                voices = []
                for voice in child:
                    assert voice.tag == "voice"

                    sentence = voice.get("sentence")
                    yell = voice.get("yell", "0")[0] in "1tTyY"
                    voices.append(Voice(sentence, yell))

                monster.voices = tuple(voices)

            case "script":
                pass

            case "loot":
                loot = []
                for item in child:
                    assert item.tag == "item"

                    id = int(item.get("id", "0"))
                    name = item.get("name")

                    chance = int(item.get("chance"))
                    assert (
                        0 <= chance <= MAX_LOOT_CHANCE
                    ), f"Chance must be between 0 and {MAX_LOOT_CHANCE}, got {chance}"

                    max_count = int(item.get("countmax", "1"))
                    assert max_count > 0, f"Invalid max count: {max_count}"

                    assert not item.get("subtype"), "loot subtype is not supported"

                    loot.append(Loot(id, name, chance / MAX_LOOT_CHANCE, max_count))

                monster.loot = tuple(loot)

            case _:
                raise ValueError(f"Invalid tag: {child.tag}")


def load_monsters(filename: PathLike) -> Generator[Monster, None, None]:
    tree = ET.parse(filename)

    root = tree.getroot()
    assert root.tag == "monsters"

    for element in root:
        assert element.tag == "monster"

        name = element.get("name")
        file = element.get("file")

        monster = load_monster(path.join(path.dirname(filename), file))
