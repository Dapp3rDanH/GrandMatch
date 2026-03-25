from dataclasses import dataclass


@dataclass
class SiblingMatch:
    cousin_name: str
    cousin_kit: str
    sibling_kit: str
    sibling_name: str
    chr: int