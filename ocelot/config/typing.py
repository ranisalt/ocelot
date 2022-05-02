from typing import Literal, Union

OptionalPvp = Union[Literal["no-pvp"], Literal["optional"]]
OpenPvp = Union[Literal["pvp"], Literal["open"]]
HardcorePvp = Union[Literal["pvp-enforced"], Literal["hardcore"]]
Pvp = Union[OptionalPvp, OpenPvp, HardcorePvp]

pvp_type_to_index: dict[str, int] = {
    "pvp": 0,
    "open": 0,
    "no-pvp": 1,
    "optional": 1,
    "pvp-enforced": 2,
    "hardcore": 2,
}
