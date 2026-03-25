from typing import Dict, List
from dataclasses import dataclass, field
from enum import Enum

from grand_match import MilestoneType, Milestone,SiblingOverlap, GrandparentSegment, Sibling

@dataclass
class OverlapCalculator:
    segment_list: List[GrandparentSegment]
    # siblingsByName: Dict[str, Sibling] = field(default_factory=dict)
    siblingsByKit: Dict[str, Sibling] = field(default_factory=dict)

    def calculate_overlaps(self):
        non_active_milestones: List[Milestone] = []
        smallest: int = 0
        largest: int = 0
        for segment in self.segment_list:
            non_active_milestones.append(Milestone(segment= segment, milestone_type= MilestoneType.START,  event_number = segment.B37_Start, is_active=False))
            non_active_milestones.append(Milestone(segment= segment, milestone_type= MilestoneType.END,  event_number = segment.B37_End, is_active=False))
            largest = max(segment.B37_End, largest)
            smallest = max(segment.B37_Start, smallest)

        sorted_milestones = sorted(non_active_milestones, key=lambda m: (m.event_number))
        overlaps = []
 
        #determine what segments are active
        activated_segments :List[GrandparentSegment] = []
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

            if len(activated_segments) > 0:
                overlap_start = max(seg.B37_Start for seg in activated_segments)
                overlap_start = max(overlap_start, active_event_number)
                chr = activated_segments[0].Chr
                grandparent = activated_segments[0].Grandparent

                overlap_segments = activated_segments[:]
                sibling_keys : List[str] = []
                for s in overlap_segments:
                    sibling_keys.append(s.Kit)

                overlap: SiblingOverlap = SiblingOverlap(segments=overlap_segments, B37_Start=overlap_start, B37_End=overlap_end, Chr=chr, Grandparent=grandparent, sibling_kits=sibling_keys)
                overlaps.append(overlap)
                #remove any segments where the end milestone were active
                for m in milestones_to_deactivate:
                    for seg in activated_segments:
                        if seg == m.segment:
                            activated_segments.remove(seg)

            active_event_number = overlap_end

        return overlaps

