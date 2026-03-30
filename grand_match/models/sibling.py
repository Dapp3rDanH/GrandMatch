from dataclasses import dataclass


@dataclass
class Sibling:
    name: str
    kit: str
    order: int = 0