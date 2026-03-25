from dataclasses import dataclass


@dataclass()
class ChromosomeSetting:
    chr: int
    mode: str = "No"