from .items.convert import convert_item
from .items.otb import load_items_otb
from .items.weapons import load_weapons_xml
from .items.xml import load_items_xml
from .map.otbm import load_map


def load_items():
    tfs_items = load_weapons_xml(
        "data/weapons/weapons.xml",
        load_items_xml("data/items/items.xml", load_items_otb("data/items/items.otb")),
    )
    return [convert_item(item) for item in tfs_items.values()]


__all__ = ["load_items", "load_map"]
