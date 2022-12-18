from ocelot.stream import Stream

from ..otb import Node, parse_otb


class ItemAttr:
    SERVER_ID = 16
    CLIENT_ID = 17
    NAME = 18
    DESCRIPTION = 19
    SPEED = 20
    SLOT = 21
    MAX_ITEMS = 22
    WEIGHT = 23
    WEAPON = 24
    AMU = 25
    ARMOR = 26
    MAGIC_LEVEL = 27
    MAGIC_FIELD_TYPE = 28
    WRITEABLE = 29
    ROTATE_TO = 30
    DECAY = 31
    SPRITE_HASH = 32
    MINIMAP_COLOR = 33
    UNKNOWN_07 = 34
    UNKNOWN_08 = 35
    LIGHT = 36

    # 1-byte aligned
    DECAY2 = 37  # deprecated
    WEAPON2 = 38  # deprecated
    AMU2 = 39  # deprecated
    ARMOR2 = 40  # deprecated
    WRITEABLE2 = 41  # deprecated
    LIGHT2 = 42
    TOP_ORDER = 43
    WRITEABLE3 = 44  # deprecated

    WARE_ID = 45


def parse_item(node: Node):
    properties = {}

    s = Stream(node.props)
    while attr := s.read_byte():
        length = s.read_int(2)

        match attr:
            case ItemAttr.SERVER_ID:
                assert (
                    length == 2
                ), f"Invalid server ID attribute length: expected 2, got {length}"

                properties["server_id"] = s.read_int(2)

            case ItemAttr.CLIENT_ID:
                assert (
                    length == 2
                ), f"Invalid client ID attribute length: expected 2, got {length}"

                properties["client_id"] = s.read_int(2)

            case ItemAttr.NAME:
                properties["name"] = s.read(length).decode("utf-8")

            case ItemAttr.DESCRIPTION:
                properties["description"] = s.read(length).decode("utf-8")

            case ItemAttr.SPEED:
                assert (
                    length == 2
                ), f"Invalid speed attribute length: expected 2, got {length}"

                properties["speed"] = s.read_int(2)

            case ItemAttr.MAX_ITEMS:
                assert (
                    length == 2
                ), f"Invalid max items attribute length: expected 2, got {length}"

                properties["max_items"] = s.read_int(2)

            case ItemAttr.WEIGHT:
                assert (
                    length == 4
                ), f"Invalid weight attribute length: expected 4, got {length}"

                properties["weight"] = s.read_double()

            case ItemAttr.ROTATE_TO:
                assert (
                    length == 2
                ), f"Invalid rotate to attribute length: expected 2, got {length}"

                properties["rotate_to"] = s.read_int(2)

            case ItemAttr.SPRITE_HASH:
                assert (
                    length == 16
                ), f"Invalid sprite hash attribute length: expected 4, got {length}"

                properties["sprite_hash"] = s.read(length)

            case ItemAttr.MINIMAP_COLOR:
                assert (
                    length == 2
                ), f"Invalid minimap color attribute length: expected 2, got {length}"

                properties["minimap_color"] = s.read_int(2)

            case ItemAttr.LIGHT2:
                assert (
                    length == 4
                ), f"Invalid light2 attribute length: expected 4, got {length}"

                properties["light_level"] = s.read_int(2)
                properties["light_color"] = s.read_int(2)

            case ItemAttr.TOP_ORDER:
                assert (
                    length == 1
                ), f"Invalid top order attribute length: expected 1, got {length}"

                properties["top_order"] = s.read_byte()

            case ItemAttr.WRITEABLE3:
                assert (
                    length == 4
                ), f"Invalid writeable3 attribute length: expected 4, got {length}"

                properties["read_only_id"] = s.read_int(2)
                properties["max_text_length"] = s.read_int(2)

            case ItemAttr.WARE_ID:
                assert (
                    length == 2
                ), f"Invalid ware ID attribute length: expected 2, got {length}"

                properties["ware_id"] = s.read_int(2)

            case ItemAttr.UNKNOWN_07 | ItemAttr.UNKNOWN_08:
                s.skip(length)

            case _:
                print(f"Unknown item attribute: {attr}")
                s.skip(length)


def load_otbi(filename: str):
    root = parse_otb(filename, b"OTBI")

    s = Stream(root.props)

    flags = s.read_int(4)
    root_attr = s.read_byte()

    assert root_attr == 1, f"Unknown root attribute: {root_attr}"

    length = s.read_int(2)
    assert (
        length == 140
    ), f"Invalid data length for version info: expected 140, got {length}"

    major, minor = s.read_int(4), s.read_int(4)
    assert (
        major == 3 and minor >= 57
    ), "Old version detected, a newer version of items.otb is required."

    return root
