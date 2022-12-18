import xml.etree.ElementTree as ET
from functools import reduce
from os import PathLike

from ocelot.tfs.items.enums import CombatType

from .base_item import BaseItem, BaseItemDict

combat_types = {
    "earth": CombatType.EARTHDAMAGE,
    "ice": CombatType.ICEDAMAGE,
    "energy": CombatType.ENERGYDAMAGE,
    "fire": CombatType.FIREDAMAGE,
    "death": CombatType.DEATHDAMAGE,
    "holy": CombatType.HOLYDAMAGE,
}

renamed_props = {
    "level": "min_level",
    "mana": "wand_mana",
    "max": "wand_max_damage",
    "min": "wand_min_damage",
    "unproperly": "can_wield_unproperly",
    "breakchance": "distance_break_chance",
}


def parse_wand(item: BaseItem, element: ET.Element) -> BaseItem:
    """Parse attributes of a wand weapon."""
    for k, v in element.attrib.items():
        match key := renamed_props.get(k, k):
            case "id":
                continue

            case "min_level" | "wand_mana" | "wand_max_damage" | "wand_min_damage":
                setattr(item, key, int(v))

            case "type":
                item.wand_combat_type = combat_types[v]

            case _:
                raise NotImplementedError(f"Unknown attribute {key}")

    return item


def parse_melee(item: BaseItem, element: ET.Element) -> BaseItem:
    """Parse attributes of a melee weapon."""
    for k, v in element.attrib.items():
        match key := renamed_props.get(k, k):
            case "id":
                continue

            case "action":
                match v.lower():
                    case "removecharge":
                        item.melee_remove_charges = True

                    case _:
                        raise NotImplementedError(f"Unknown melee action {v}")

            case "can_wield_unproperly":
                setattr(item, key, v[0] in "1tTyY")

            case "min_level":
                setattr(item, key, int(v))

            case _:
                raise NotImplementedError(f"Unknown attribute {key}")

    return item


def parse_distance(item: BaseItem, element: ET.Element) -> BaseItem:
    """Parse attributes of a distance weapon."""
    for k, v in element.attrib.items():
        match key := renamed_props.get(k, k):
            case "id":
                continue

            case "action":
                match v.lower():
                    case "removecount":
                        item.distance_remove_count = True

                    case _:
                        raise NotImplementedError(f"Unknown melee action {v}")

            case "can_wield_unproperly":
                setattr(item, key, v[0] in "1tTyY")

            case "min_level" | "distance_break_chance":
                setattr(item, key, int(v))

            case "script":
                setattr(item, key, v)

            case _:
                raise NotImplementedError(f"Unknown attribute {key}")

    return item


tag_parser = {
    "wand": parse_wand,
    "melee": parse_melee,
    "distance": parse_distance,
}


def parse_vocations(element: ET.Element):
    for v in element:
        assert v.tag == "vocation"
        yield v.attrib["name"].lower()


def parse_weapon(items: BaseItemDict, element: ET.Element):
    item_id = int(element.attrib["id"])

    item = items[item_id]
    item.vocations = {*parse_vocations(element)}
    parser = tag_parser[element.tag]
    items[item_id] = parser(item, element)
    return items


def load_weapons_xml(path: PathLike, items: BaseItemDict) -> BaseItemDict:
    tree = ET.parse(path)

    root = tree.getroot()
    assert root.tag == "weapons"

    return reduce(parse_weapon, root, items)
