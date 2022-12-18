from os import PathLike, path

from .items.convert import convert_item
from .items.otb import load_items_otb
from .items.weapons import load_weapons_xml
from .items.xml import load_items_xml
from .map.otbm import load_map
from .monsters import load_monsters


def load_tfs(basedir: PathLike):
    """Load TFS data from a directory."""
    items = {
        id: convert_item(item)
        for id, item in load_weapons_xml(
            path.join(basedir, "weapons/weapons.xml"),
            load_items_xml(
                path.join(basedir, "items/items.xml"),
                load_items_otb(path.join(basedir, "items/items.otb")),
            ),
        ).items()
    }
    monsters = load_monsters(path.join(basedir, "monster/monsters.xml"))
    map = load_map(path.join(basedir, "world/forgotten.otbm"))
    return items, monsters, map


tfs = load_tfs("./data")
