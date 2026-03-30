from dataclasses import dataclass

from grand_match import MilestoneType, GrandparentSegment


@dataclass
class Milestone:
    segment: GrandparentSegment
    milestone_type: MilestoneType
    event_number: int = 0
    is_active: bool = False
