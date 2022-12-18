import struct
from functools import reduce
from os import PathLike

from ocelot.stream import Stream

from ..otb import Node, parse_otb
from .base_item import BaseItem, BaseItemDict
from .enums import ItemGroup, ItemType

mapped_props = {
    16: "server_id",  # server id
    17: "client_id",
    18: "name",
    19: "description",
    20: "speed",
    22: "max_items",
    23: "weight",
    30: "rotate_to",
    31: "decay",
    32: "sprite_hash",
    33: "minimap_color",
    34: "unknown",  # tfs calls this "07"
    35: "unknown",  # tfs calls this "08"
    42: "light",  # light2
    43: "always_on_top_order",
    44: "writeable",  # writeable3
    45: "ware_id",
    46: "classification",
}

item_group_to_type = {
    ItemGroup.CONTAINER: ItemType.CONTAINER,
    ItemGroup.DOOR: ItemType.DOOR,
    ItemGroup.MAGIC_FIELD: ItemType.MAGIC_FIELD,
    ItemGroup.TELEPORT: ItemType.TELEPORT,
}


def parse_item_node(items: BaseItemDict, node: Node) -> BaseItemDict:
    stream = Stream(node.props)
    flags = stream.read_int(4)

    item = BaseItem(flags=flags)

    while attr := stream.read_byte():
        length = stream.read_int(2)

        match key := mapped_props.get(attr, "unknown"):
            case "always_on_top_order" | "classification":
                assert (
                    length == 1
                ), f"Invalid {key} attribute length: expected 1, got {length}."

                setattr(item, key, stream.read_int(length))

            case "server_id" | "client_id" | "speed" | "max_items" | "rotate_to" | "minimap_color" | "ware_id":
                assert (
                    length == 2
                ), f"Invalid {key} attribute length: expected 2, got {length}."

                setattr(item, key, stream.read_int(length))

            case "name" | "description":
                setattr(item, key, stream.read(length).decode("unicode_escape"))

            case "light":
                assert (
                    length == 4
                ), f"Invalid {key} attribute length: expected 4, got {length}."

                item.light_level = stream.read_int(2)
                item.light_color = stream.read_int(2)

            case "sprite_hash":
                assert (
                    length == 16
                ), f"Invalid {key} attribute length: expected 16, got {length}."

                setattr(item, "sprite_hash", stream.read(length))

            case "weight":
                assert (
                    length == 8
                ), f"Invalid {key} attribute length: expected 8, got {length}."

                item.weight, *_ = struct.unpack("<d", stream.read(8))

            case "writeable":
                assert (
                    length == 4
                ), f"Invalid {key} attribute length: expected 4, got {length}."

                item.read_only_item_id = stream.read_int(2)
                item.max_text_length = stream.read_int(2)

            case "unknown":  # unsupported attributes
                # print(
                #     f"[Warning] Unsupported attribute {key} ({attr}) length {length}."
                # )
                stream.skip(length)

    assert item.server_id, "Invalid item server ID."
    assert item.client_id, "Invalid item client ID."

    if node.type:
        item.group = ItemGroup(node.type)
        item.item_type = item_group_to_type.get(item.group)

    items[item.server_id] = item
    return items


def load_items_otb(path: PathLike) -> BaseItemDict:
    otb = parse_otb(path, b"OTBI")

    loader = Stream(otb.props)

    # flags = loader.read(4)  # unused
    loader.skip(4)

    root_attr = loader.read(1)
    assert root_attr == b"\x01"

    version_length = int.from_bytes(loader.read(2), "little")
    assert (
        version_length == 140
    ), f"Invalid data length for version info: expected 140, got {version_length}."

    major = int.from_bytes(loader.read(4), "little")
    minor = int.from_bytes(loader.read(4), "little")
    build = int.from_bytes(loader.read(4), "little")
    csd_version = loader.read(128)
    print(
        f"OTB version {major}.{minor}.{build} ({csd_version.decode('unicode_escape')})"
    )

    assert (
        major == 3 or major == 0xFFFFFFFF
    ), "Old major version detected, a newer version of items.otb is required."

    assert (
        minor >= 57
    ), "Old minor version detected, a newer version of items.otb is required."

    if major == 0xFFFFFFFF:
        print("[Warning] items.otb using generic client version.")

    return reduce(parse_item_node, otb.children, {})
