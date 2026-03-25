from dataclasses import dataclass, field
from typing import List

from grand_match import GrandparentSegment


@dataclass
class SiblingOverlap:
    Chr: int
    # Siblings: str
    Grandparent: str  
    B37_Start: int
    B37_End: int
    sibling_kits: List[str] = field(default_factory=list)
    segments: List[GrandparentSegment] = field(default_factory=list)