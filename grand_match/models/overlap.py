
from dataclasses import dataclass, field
from typing import List

from grand_match import Segment


@dataclass
class Overlap:
    segments: List[Segment] = field(default_factory=list)
    start: int = None
    end: int = None
