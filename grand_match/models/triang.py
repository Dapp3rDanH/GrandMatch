from dataclasses import dataclass


@dataclass
class Triang:
    Chr: int
    Kit1_Number: str
    Kit1_Name: str
    Kit1_Email: str
    Kit2_Number: str
    Kit2_Name: str
    Kit2_Email: str
    B37_Start: int
    B37_End: int
    cM: str
    grandparent: str = "Unknown"
    source_sibling: str = "Unknown"