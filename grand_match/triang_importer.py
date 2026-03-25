import csv
from dataclasses import dataclass
import fnmatch
import os
from typing import List

from grand_match import Triang


@dataclass
class TriagImporter:
    def importCsv(self, directory: str):
        for root, dirs, files in os.walk(directory):
            for filename in fnmatch.filter(files, '*.csv'):
                file_path: str = os.path.join(root, filename)
                triang_list = self.createList(file_path)
                # print(file_path)
                # print(triang_list)

    def createList(self, file_path: str) -> List[Triang]:
        triang_list = []
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                chr_string = (row["Chr"])
                if chr_string == "X":
                    chr_string = 23
                triang = Triang(int(chr_string), row["Kit1 Number"], row["Kit1 Name"], row["Kit1 Email"], row["Kit2 Number"], row["Kit2 Name"], row["Kit2 Email"], int(row["B37 Start"]), int(row["B37 End"]), row["cM"])
                triang_list.append(triang)
        return triang_list
