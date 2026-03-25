from grand_match.models.segment import Segment
from grand_match.overlap_calculatorOld import OverlapCalculatorOld


segments = [
    Segment("Dale", 25898921, 180690937),
    Segment("Debbie", 34948532, 90620309),
    Segment("Debbie", 127248485, 163633239),
    Segment("Donal", 0, 33000000),
    Segment("Donal", 81917419, 148700714),
    Segment("Dennis", 108638291, 180690937),
    Segment("Diane", 0, 180690937)
]

calculator = OverlapCalculatorOld(segments)
overlaps = calculator.calculate_overlaps()

for overlap in overlaps:
    print(f"Overlap from {overlap.start} to {overlap.end} between segments:")
    for seg in overlap.segments:
        print(f"  - {seg.name} ({seg.start} to {seg.end})")
