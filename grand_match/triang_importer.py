import csv
from dataclasses import dataclass
from typing import List

from grand_match import Triang


@dataclass
class TriagImporter:
    def createList(self, file_path: str, enabled_chromosomes: set = None) -> List[Triang]:
        triang_list = []
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                chr_string = (row["Chr"])
                if chr_string == "X":
                    chr_string = 23
                chr_int = int(chr_string)
                if enabled_chromosomes is not None and chr_int not in enabled_chromosomes:
                    continue
                triang = Triang(chr_int, row["Kit1 Number"], row["Kit1 Name"], row["Kit1 Email"], row["Kit2 Number"], row["Kit2 Name"], row["Kit2 Email"], int(row["B37 Start"]), int(row["B37 End"]), row["cM"])
                triang_list.append(triang)
        return triang_list
