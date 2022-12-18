from dataclasses import dataclass
from os import PathLike, path
from typing import Any, Generator, Mapping, Sequence

from ocelot.stream import Stream
from ocelot.world.map import Map, Position, Tile, Town

from ..otb import Node, parse_otb
from .enums import Attribute, NodeType
from .houses import House, load_houses
from .spawns import Spawn, load_spawns


@dataclass(slots=True)
class MapHeader:
    header_version: int
    width: int
    height: int
    major_version: int
    minor_version: int


@dataclass(slots=True)
class MapAttributes:
    description: str
    spawn_file: str
    house_file: str


def parse_map_header(data: bytes) -> MapHeader:
    s = Stream(data)

    header_version = s.read_int(4)

    assert (
        header_version != 0
    ), "This map need to be upgraded by using the latest map editor version to be able to load correctly."

    assert header_version <= 2, "Unknown OTBM version detected."

    width = s.read_int(2)
    height = s.read_int(2)

    major_version = s.read_int(4)
    minor_version = s.read_int(4)

    assert (
        major_version >= 3
    ), "This map need to be upgraded by using the latest map editor version to be able to load correctly."

    assert minor_version >= 8, "This map needs to be updated."

    return MapHeader(
        header_version=header_version,
        width=width,
        height=height,
        major_version=major_version,
        minor_version=minor_version,
    )


def parse_map_attributes(data: bytes) -> MapAttributes:
    s = Stream(data)

    properties = {}
    while byte := s.read_byte(1):
        match byte:
            case Attribute.MAP_DESCRIPTION:
                properties["description"] = s.read_string()

            case Attribute.MAP_SPAWN_FILE:
                properties["spawn_file"] = s.read_string()

            case Attribute.MAP_HOUSE_FILE:
                properties["house_file"] = s.read_string()

            case _:
                raise Exception(f"Unknown map attribute: {byte}.")

    return MapAttributes(**properties)


@dataclass(slots=True)
class TileArea:
    position: Position
    children: bytes


@dataclass(slots=True)
class Waypoint:
    name: str
    position: Position


class TileFlag:
    ProtectionZone = 1 << 0
    NoPvpZone = 1 << 2
    NoLogout = 1 << 3
    PvpZone = 1 << 4


def parse_tile_area(tile: Node):
    assert len(tile.props) == 5, f"Invalid tile area props length: {len(tile.props)}"

    s = Stream(tile.props)

    origin_x, origin_y, z = s.read_coords()
    for tile in tile.children:
        assert (
            tile.type == NodeType.TILE or tile.type == NodeType.HOUSE_TILE
        ), f"Unknown tile area node type: {tile.type}"

        s = Stream(tile.props)

        x, y = origin_x + s.read_byte(), origin_y + s.read_byte()
        house_id = s.read_int(4) if tile.type == NodeType.HOUSE_TILE else None

        position = Position(x=x, y=y, z=z)
        tile_properties: dict[str, Any] = {"items": []}
        while attr := s.read_byte():
            match attr:
                case Attribute.TILE_FLAGS:
                    flags = s.read_int(4)

                    if flags & TileFlag.ProtectionZone:
                        tile_properties["protection_zone"] = True

                    if flags & TileFlag.NoPvpZone:
                        tile_properties["no_pvp_zone"] = True

                    if flags & TileFlag.NoLogout:
                        tile_properties["no_logout"] = True

                    if flags & TileFlag.PvpZone:
                        tile_properties["pvp_zone"] = True

                case Attribute.ITEM:
                    assert (
                        "ground_item" not in tile_properties
                    ), "Duplicate ground item attribute."

                    tile_properties["ground_item"] = s.read_int(2)

                case _:
                    raise Exception(
                        f"Unknown tile attribute {attr} at ({x}, {y}, {z})."
                    )

        for item in tile.children:
            assert (
                item.type == NodeType.ITEM
            ), f"Unknown tile area item type: {item.type}"

            s = Stream(item.props)

            item_properties: dict[str, Any] = {"item_id": s.read_int(2)}
            while attr := s.read_byte():
                match attr:
                    case Attribute.CHARGES:
                        item_properties["charges"] = s.read_byte()

                    case Attribute.COUNT:
                        item_properties["count"] = s.read_byte()

                    case Attribute.RUNE_CHARGES:
                        item_properties["rune_charges"] = s.read_byte()

                    case Attribute.ACTION_ID:
                        item_properties["action_id"] = s.read_int(2)

                    case Attribute.UNIQUE_ID:
                        item_properties["unique_id"] = s.read_int(2)

                    case Attribute.TEXT:
                        item_properties["text"] = s.read_string()

                    case Attribute.WRITTEN_DATE:
                        item_properties["written_date"] = s.read_int(4)

                    case Attribute.WRITTEN_BY:
                        item_properties["written_by"] = s.read_string()

                    case Attribute.DESCRIPTION:
                        item_properties["description"] = s.read_string()

                    case Attribute.DURATION:
                        item_properties["duration"] = max(0, s.read_int(4))

                    case Attribute.DECAYING_STATE:
                        item_properties["decay_state"] = s.read_byte()

                    case Attribute.ARTICLE:
                        item_properties["article"] = s.read_string()

                    case Attribute.PLURAL_NAME:
                        item_properties["plural_name"] = s.read_string()

                    case Attribute.WEIGHT:
                        item_properties["weight"] = s.read_int(4)

                    case Attribute.ATTACK:
                        item_properties["attack"] = s.read_int(4)

                    case Attribute.DEFENSE:
                        item_properties["defense"] = s.read_int(4)

                    case Attribute.EXTRA_DEFENSE:
                        item_properties["extra_defense"] = s.read_int(4)

                    case Attribute.ARMOR:
                        item_properties["armor"] = s.read_int(4)

                    case Attribute.HIT_CHANCE:
                        item_properties["hit_chance"] = s.read_byte()

                    case Attribute.SHOOT_RANGE:
                        item_properties["shoot_range"] = s.read_byte()

                    case Attribute.DECAY_TO:
                        item_properties["decay_to"] = s.read_int(4)

                    case Attribute.WRAP_ID:
                        item_properties["wrap_id"] = s.read_int(2)

                    case Attribute.STORE_ITEM:
                        item_properties["store_item"] = s.read_byte()

                    case Attribute.DEPOT_ID:
                        item_properties["depot_id"] = s.read_int(2)

                    case Attribute.HOUSE_DOOR_ID:
                        item_properties["house_door_id"] = s.read_int(1)

                    case Attribute.SLEEPER_GUID:
                        item_properties["sleeper_guid"] = s.read_int(4)

                    case Attribute.SLEEPER_START:
                        item_properties["sleep_start"] = s.read_int(4)

                    case Attribute.TELEPORT_DESTINATION:
                        item_properties["tele_dest"] = s.read_coords()

                    case Attribute.CUSTOM_ATTRIBUTES:
                        length = s.read_int(4)

                        for i in range(length):
                            key = s.read_string()

                            match value_type := s.read_byte():
                                case 1:
                                    item_properties[key] = s.read_string()

                                case 2:
                                    item_properties[key] = s.read_int(8, signed=True)

                                case 3:
                                    item_properties[key] = s.read_double(8)

                                case 4:
                                    item_properties[key] = s.read_byte() != 0

                                case _:
                                    raise Exception(
                                        f"Unknown custom attribute type: {value_type}"
                                    )

                    case _:
                        raise Exception(
                            f"Unknown item attribute {attr} at ({x}, {y}, {z}, bytes: {s.read()})."
                        )

            tile_properties["items"].append(item_properties)

        yield position, Tile(ground_item=tile_properties["ground_item"])


def parse_towns(node: Node) -> Generator[Town, None, None]:
    for town in node.children:
        assert town.type == NodeType.TOWN, f"Unknown town node type: {town.type}"

        s = Stream(town.props)
        yield Town(
            id=s.read_byte(4),
            name=s.read_string(),
            temple_position=Position(*s.read_coords()),
        )


def parse_waypoints(node: Node) -> Generator[Waypoint, None, None]:
    for waypoint in node.children:
        assert (
            waypoint.type == NodeType.WAYPOINT
        ), f"Unknown waypoint node type: {waypoint.type}"

        s = Stream(waypoint.props)
        yield Waypoint(name=s.read_string(), position=Position(*s.read_coords()))


# @dataclass(slots=True)
# class Map:
#     width: int
#     height: int

#     description: str
#     spawns: tuple[Spawn]
#     houses: tuple[House]

#     towns: tuple[Town]
#     waypoints: tuple[Waypoint]
#     tiles: dict[Position, Tile]


def load_map(filename: str) -> Map:
    root = parse_otb(filename, b"OTBM")

    # assert root.type == NodeType.RootV1, f"Unknown root node type: {root.type}"
    assert len(root.children) == 1, "Expected exactly one tree node."

    map_header = parse_map_header(root.props)
    print(f"> Map size: {map_header.width}x{map_header.height}.")

    map_data = root.children[0]
    assert (
        map_data.type == NodeType.MAP_DATA
    ), f"Unknown map data node type: {map_data.type}"

    map_attributes = parse_map_attributes(map_data.props)

    print(">> Description:", map_attributes.description)
    print(">> Spawn file:", map_attributes.spawn_file)
    print(">> House file:", map_attributes.house_file)

    tiles: dict[Position, Tile] = {}
    towns: list[Town] = []
    waypoints: list[Waypoint] = []
    for node in map_data.children:
        match node.type:
            case NodeType.TILE_AREA:
                tiles.update(parse_tile_area(node))

            case NodeType.TOWNS:
                towns.extend(parse_towns(node))

            case NodeType.WAYPOINTS:
                waypoints.extend(parse_waypoints(node))

            case _:
                raise Exception(f"Unknown map node type: {node.type}.")

    print(
        f">> Loaded {len(tiles)} tiles, {len(towns)} towns, {len(waypoints)} waypoints."
    )

    return Map(
        # width=map_header.width,
        # height=map_header.height,
        # description=map_attributes.description,
        # spawns=tuple(
        #     load_spawns(path.join(path.dirname(filename), map_attributes.spawn_file))
        # ),
        # houses=tuple(
        #     load_houses(path.join(path.dirname(filename), map_attributes.house_file))
        # ),
        tiles=tiles,
        towns=towns,
        # waypoints=tuple(waypoints),
    )
