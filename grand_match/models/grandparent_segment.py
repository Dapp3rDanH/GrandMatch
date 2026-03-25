from dataclasses import dataclass


@dataclass
class GrandparentSegment:
    Chr: int
    Sibling: str
    Kit: str
    Grandparent: str  
    B37_Start: int
    B37_End: int
