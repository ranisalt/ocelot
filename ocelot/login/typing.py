from typing import Literal, Union

OptionalPvp = Union[Literal["no-pvp"], Literal["optional"]]
OpenPvp = Union[Literal["pvp"], Literal["open"]]
HardcorePvp = Union[Literal["pvp-enforced"], Literal["hardcore"]]
Pvp = Union[OptionalPvp, OpenPvp, HardcorePvp]
