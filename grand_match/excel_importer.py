from dataclasses import dataclass, field
from typing import Dict, List
import pandas as pd
from grand_match import ChromosomeSetting, Cousin, Grandparent, GrandparentSegment, Sibling


@dataclass()
class ExcelImporter:
    excel_file_full_path: str
    siblingsByName: Dict[str, Sibling] = field(default_factory=dict)
    siblingsByKit: Dict[str, Sibling] = field(default_factory=dict)
    grandparentsByName: Dict[str, Grandparent] = field(default_factory=dict)
    grandparentsByKit: Dict[str, Grandparent] = field(default_factory=dict)
    cousinByName: Dict[str, Cousin] = field(default_factory=dict)
    cousinByKit: Dict[str, Cousin] = field(default_factory=dict)
    grandparent_segments: List[GrandparentSegment] = field(default_factory=list)
    chromosome_settings_by_chr: Dict[int, ChromosomeSetting] = field(default_factory=dict)

    def importExcel(self):
        self.import_chromosome_settings()
        self.importSiblings()
        self.importCousins()
        self.importGrandparents()
        self.importGrandparentSegments()

    def import_chromosome_settings(self):
        siblings_df = pd.read_excel(self.excel_file_full_path, sheet_name='chromosomes', header=0, engine='openpyxl')

        for index, row in siblings_df.iterrows():
            chr_as_str = row['Chr']
            chr: int = int(chr_as_str)

            mode = row['Mode'].strip()
      
            if chr not in self.chromosome_settings_by_chr:
                setting = ChromosomeSetting(chr=chr, mode=mode)
                self.chromosome_settings_by_chr[chr] = setting

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
            mode = str(row.get('Mode', 'Yes')).strip()
            if mode.lower() != 'yes':
                continue

            grandparent = Grandparent(name=name)
            self.grandparentsByName.setdefault(name, grandparent)

    def importSiblings(self):
        siblings_df = pd.read_excel(self.excel_file_full_path, sheet_name='Siblings', header=0, engine='openpyxl')

        for index, row in siblings_df.iterrows():
            name = row['Name'].strip()
            kit = row['Kit'].strip()
            order = int(row.get('Order', 0) or 0)

            sibling = Sibling(name=name, kit=kit, order=order)
            self.siblingsByName.setdefault(name, sibling)
            self.siblingsByKit.setdefault(kit, sibling)

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
