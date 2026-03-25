from dataclasses import dataclass, field
from typing import Dict, List

from grand_match import Triang


@dataclass()
class TriangGroup:
    chr: str = "NA"
    kit_Number: str = "NA"
    B37_Start: int = 0
    B37_End: int = 0
    triang_list: List[Triang] = field(default_factory=list)
    siblingKitCountGroup: Dict[str,int] = field(default_factory=dict)
    groupContainsExcludedCousin: bool = False

    def reset(self, kit_number: str, chr: str):
        #reset all group related symbols
        self.kit_Number = kit_number
        self.chr = chr
        self.groupContainsExcludedCousin = False
        self.siblingKitCountGroup = {}
        self.triang_list = []