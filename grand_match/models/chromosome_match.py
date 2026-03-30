from dataclasses import dataclass


@dataclass
class ChromosomeMatch:
    name: str
    kit: str
    grandparent: str
    chr: int
    platform: str = ""
    siblings: str = ""