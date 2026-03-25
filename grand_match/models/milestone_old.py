from dataclasses import dataclass
from enum import Enum

from grand_match import Segment, MilestoneType

@dataclass
class MilestoneOld:
    segment: Segment
    milestone_type: MilestoneType
    event_number: int = 0
    is_active: bool = False

