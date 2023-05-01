from typing import List
from dataclasses import dataclass, field
from enum import Enum

@dataclass
class Segment:
    name: str
    start: int
    end: int


@dataclass
class Overlap:
    segments: List[Segment] = field(default_factory=list)
    start: int = None
    end: int = None

class MilestoneType(Enum):
    START = 1
    END = 2

@dataclass
class Milestone:
    segment: Segment
    milestone_type: MilestoneType
    event_number: int = 0
    is_active: bool = False


@dataclass
class OverlapCalculator:
    segment_list: List[Segment]

    def calculate_overlaps(self):
        non_active_milestones: List[Milestone] = []
        smallest: int = 0
        largest: int = 0
        for segment in self.segment_list:
            non_active_milestones.append(Milestone(segment= segment, milestone_type= MilestoneType.START,  event_number = segment.start, is_active=False))
            non_active_milestones.append(Milestone(segment= segment, milestone_type= MilestoneType.END,  event_number = segment.end, is_active=False))
            largest = max(segment.end, largest)
            smallest = max(segment.start, smallest)

        sorted_milestones = sorted(non_active_milestones, key=lambda m: (m.event_number))
        overlaps = []
 
        #determine what segments are active
        activated_segments :List[Segment] = []
        active_event_number:int = 0
        while active_event_number < largest:
            for m in sorted_milestones:
                if m.event_number > active_event_number:
                    break
                if m.is_active == False and m.event_number == active_event_number:
                    m.is_active = True
                    activated_segments.append(m.segment)


            overlap_end: int
            #find the first non-activated milestone
            for m in sorted_milestones:
                if m.is_active == False:
                    overlap_end = m.event_number
                    break
            #if this milestone is Type=End, then lets remove the segment after creating overlap
            milestones_to_deactivate : List[segment] = []
            for m in sorted_milestones:
                if m.milestone_type == MilestoneType.END and m.event_number == overlap_end:
                    m.is_active = True
                    milestones_to_deactivate.append(m)

            overlap_start = max(seg.start for seg in activated_segments)
            overlap_start = max(overlap_start, active_event_number)
            overlap: Overlap = Overlap(segments=activated_segments[:], start=overlap_start, end=overlap_end)
            overlaps.append(overlap)
            #remove any segments where the end milestone was active
            for m in milestones_to_deactivate:
                for seg in activated_segments:
                    if seg == m.segment:
                        activated_segments.remove(seg)

            active_event_number = overlap_end

        return overlaps

segments = [
    Segment("Dale", 25898921, 180690937),
    Segment("Debbie", 34948532, 90620309),
    Segment("Debbie", 127248485, 163633239),
    Segment("Donal", 0, 33000000),
    Segment("Donal", 81917419, 148700714),
    Segment("Dennis", 108638291, 180690937),
    Segment("Diane", 0, 180690937)
]

calculator = OverlapCalculator(segments)
overlaps = calculator.calculate_overlaps()

for overlap in overlaps:
    print(f"Overlap from {overlap.start} to {overlap.end} between segments:")
    for seg in overlap.segments:
        print(f"  - {seg.name} ({seg.start} to {seg.end})")
