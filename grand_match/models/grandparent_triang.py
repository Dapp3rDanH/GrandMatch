from dataclasses import dataclass

from grand_match import Triang


@dataclass
class GrandparentTriang(Triang):
    grandparent: str