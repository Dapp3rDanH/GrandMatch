from dataclasses import dataclass


@dataclass
class Segment:
    name: str
    start: int
    end: int