from typing import List
from dataclasses import dataclass, field


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


@dataclass
class OverlapCalculator:
    segment_list: List[Segment]

    def calculate_overlaps(self) -> List[Overlap]:
        overlaps = []
        for i in range(len(self.segment_list)):
            for j in range(i+1, len(self.segment_list)):
                segment_subset = self.segment_list[i:j+1]
                overlap_start = max(seg.start for seg in segment_subset)
                overlap_end = min(seg.end for seg in segment_subset)
                if overlap_start <= overlap_end:
                    overlap_segments = [seg for seg in segment_subset if seg.start <= overlap_end and seg.end >= overlap_start]
                    overlaps.append(Overlap(segments=overlap_segments, start=overlap_start, end=overlap_end))
        return overlaps

segments = [
    Segment("Segment1", 25898921, 180690937),
    Segment("Segment2", 34948532, 90620309),
    Segment("Segment3", 127248485, 163633239),
    Segment("Segment4", 0, 23000000),
    Segment("Segment5", 81917419, 148700714),
    Segment("Segment6", 10863291, 180690937),
    Segment("Segment7", 0, 180690937)
]

calculator = OverlapCalculator(segments)
overlaps = calculator.calculate_overlaps()

for overlap in overlaps:
    print(f"Overlap from {overlap.start} to {overlap.end} between segments:")
    for seg in overlap.segments:
        print(f"  - {seg.name} ({seg.start} to {seg.end})")
