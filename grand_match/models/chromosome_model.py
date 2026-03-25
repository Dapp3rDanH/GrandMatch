from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List

from grand_match import GrandparentSegment, SiblingOverlap, Triang

if TYPE_CHECKING:
    from grand_match import GrandMatch

@dataclass()
class ChromosomeModel:
    grand_match: "GrandMatch"
    chr: int
    segmentsByGrandparent: Dict[str, List[GrandparentSegment]] = field(default_factory=dict)
    overlapsByGrandparent: Dict[str, List[SiblingOverlap]] = field(default_factory=dict)
    triangBySibling: Dict[str, List[Triang]] = field(default_factory=dict)

    def __post_init__(self):
        pass