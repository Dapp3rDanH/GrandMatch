from dataclasses import dataclass, field
from typing import Dict, List
import pandas as pd
from triangulation import Cousin, Grandparent, GrandparentSegment, Sibling, SiblingOverlap


@dataclass
class ExcelImporter:
    excel_file_full_path: str
    siblingsByName: Dict[str, Sibling] = field(default_factory=dict)
    siblingsByKit: Dict[str, Sibling] = field(default_factory=dict)
    grandparentsByName: Dict[str, Grandparent] = field(default_factory=dict)
    grandparentsByKit: Dict[str, Grandparent] = field(default_factory=dict)
    cousinByName: Dict[str, Cousin] = field(default_factory=dict)
    cousinByKit: Dict[str, Cousin] = field(default_factory=dict)
    grandparent_segments: List[GrandparentSegment] = field(default_factory=list)
    overlaps : List[SiblingOverlap] = field(default_factory=list)

    def importExcel(self):
        self.importSiblings()
        self.importCousins()
        self.importGrandparents()
        self.importGrandparentSegments()

    def importCousins(self):
        siblings_df = pd.read_excel(self.excel_file_full_path, sheet_name='Cousins', header=0, engine='openpyxl')

        for index, row in siblings_df.iterrows():
            name = row['Name'].strip()
            kit = row['Kit'].strip()
            grandparent = row["Grandparent"]

            cousin = Cousin(name=name,kit=kit, grandparent=grandparent)
            self.cousinByName.setdefault(name, cousin)
            self.cousinByKit.setdefault(kit,cousin)

    def importGrandparents(self):
        siblings_df = pd.read_excel(self.excel_file_full_path, sheet_name='Grandparents', header=0, engine='openpyxl')

        for index, row in siblings_df.iterrows():
            name = row['Name'].strip()

            grandparent = Grandparent(name=name)
            self.grandparentsByName.setdefault(name, grandparent)

    def importSiblings(self):
        siblings_df = pd.read_excel(self.excel_file_full_path, sheet_name='Siblings', header=0, engine='openpyxl')

        for index, row in siblings_df.iterrows():
            name = row['Name'].strip()
            kit = row['Kit'].strip()

            sibling = Sibling(name=name, kit=kit)
            self.siblingsByName.setdefault(name, sibling)
            self.siblingsByKit.setdefault(kit, sibling)

    def importSiblingOverlap(self):
        siblings_df = pd.read_excel(self.excel_file_full_path, sheet_name='SiblingOverlaps', header=0, engine='openpyxl')

        for index, row in siblings_df.iterrows():
            chromosome = row['Chr']
            siblingNames = row['Siblings']
            grandparent = row['Grandparent']
            start = int(row['B37 Start'])
            end = int(row['B37 End'])
            siblingOverlap = SiblingOverlap(chromosome, siblingNames, grandparent, start, end)

            name_list = siblingNames.split('|')
            name_list = [name.strip() for name in name_list]
            for x in name_list:
                if x in self.siblingsByName:
                    sibling: Sibling = self.siblingsByName[x]
                    siblingOverlap.siblings_list.append(sibling)
                    siblingOverlap.sibling_kits.append(sibling.kit)

            self.overlaps.append(siblingOverlap)

    def importGrandparentSegments(self):
        siblings_df = pd.read_excel(self.excel_file_full_path, sheet_name='GrandparentSegments', header=0, engine='openpyxl')

        for index, row in siblings_df.iterrows():
            chromosome = row['Chr']
            sibling = row['Sibling']
            kit = row['Kit']
            grandparent = row['Grandparent']
            start = int(row['B37 Start'])
            end = int(row['B37 End'])
            segment = GrandparentSegment(chromosome, sibling, kit, grandparent, start, end)

            self.grandparent_segments.append(segment)