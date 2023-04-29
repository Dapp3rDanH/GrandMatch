import csv
import os
import fnmatch
from dataclasses import dataclass, field
import pandas as pd
from typing import Dict, List



@dataclass
class GrandparentSegment:
    Chr: str
    Sibling: str
    Kits: str
    Grandparent: str  
    B37_Start: int
    B37_End: int


@dataclass
class Triang:
    Chr: str
    Kit1_Number: str
    Kit1_Name: str
    Kit1_Email: str
    Kit2_Number: str
    Kit2_Name: str
    Kit2_Email: str
    B37_Start: int
    B37_End: int
    cM: str
    

@dataclass
class Sibling:
    name: str
    kit: str

@dataclass
class Grandparent:
    name: str

@dataclass
class Cousin:
    name: str
    kit: str
    grandparent: str

@dataclass
class SiblingOverlap:
    Chr: str
    # Siblings: str
    Grandparent: str  
    B37_Start: int
    B37_End: int
    siblings_list: List[Sibling] = field(default_factory=list)
    sibling_keys: List[str] = field(default_factory=list)
    segments: List[GrandparentSegment] = field(default_factory=list)


@dataclass
class OverlapCalculator:
    segment_list: List[GrandparentSegment]

    def calculate_overlaps(self) -> List[SiblingOverlap]:
        overlaps = []
        for i in range(len(self.segment_list)):
            for j in range(i+1, len(self.segment_list)):
                segment_subset = self.segment_list[i:j+1]
                overlap_start = max(seg.B37_Start for seg in segment_subset)
                overlap_end = min(seg.B37_End for seg in segment_subset)
                chr = segment_subset[0].Chr
                grandparent = segment_subset[0].Grandparent
                if overlap_start <= overlap_end:
                    overlap_segments = [seg for seg in segment_subset if seg.B37_Start <= overlap_end and seg.B37_End >= overlap_start]
                    overlaps.append(SiblingOverlap(segments=overlap_segments, B37_Start=overlap_start, B37_End=overlap_end, Chr=chr,Grandparent=grandparent))
        return overlaps


@dataclass
class ExcelImporter:
    directory: str
    siblingsByName: Dict[str, Sibling] = field(default_factory=dict)
    siblingsByKit: Dict[str, Sibling] = field(default_factory=dict)
    grandparentsByName: Dict[str, Grandparent] = field(default_factory=dict)
    grandparentsByKit: Dict[str, Grandparent] = field(default_factory=dict)
    cousinByName: Dict[str, Cousin] = field(default_factory=dict)
    cousinByKit: Dict[str, Cousin] = field(default_factory=dict)
    overlaps : List[SiblingOverlap] = field(default_factory=list)
    grandparent_segments: List[GrandparentSegment] = field(default_factory=list)
    sibling_overlap_by_chr: Dict[str, SiblingOverlap] = field(default_factory=dict)

    def importExcel(self):
        self.importSiblings()
        self.importCousins()
        self.importGrandparents()
        # self.importSiblingOverlap()
        self.importGrandparentSegments()
        calculator = OverlapCalculator(self.grandparent_segments)
        overlaps = calculator.calculate_overlaps()


        sibling_overlap_by_chr = {}

        # loop over the SiblingOverlap instances in the list
        for sib_overlap in overlaps:
            # get the chromosome name
            chr_name = sib_overlap.Chr
            
            # if the chromosome name is not already a key in the dictionary, add it with an empty list as the value
            if chr_name not in sibling_overlap_by_chr:
                sibling_overlap_by_chr[chr_name] = []
            
            # add the SiblingOverlap instance to the list associated with the chromosome name
            sibling_overlap_by_chr[chr_name].append(sib_overlap)


        for chr in sibling_overlap_by_chr.keys():
            overlaps = sibling_overlap_by_chr[chr]
            for overlap in overlaps:
                print(f"Chr {chr} Overlap from {overlap.B37_Start} to {overlap.B37_End} between segments:")
                for seg in overlap.segments:
                    print(f"  - {seg.Sibling} ({seg.B37_Start} to {seg.B37_End})")




    def importCousins(self):
        siblings_df = pd.read_excel('visualphasing.xlsx', sheet_name='Cousins', header=0, engine='openpyxl')

        for index, row in siblings_df.iterrows():
            name = row['Name'].strip()
            kit = row['Kit'].strip()
            grandparent = row["Grandparent"]

            cousin = Cousin(name=name,kit=kit, grandparent=grandparent)
            self.cousinByName.setdefault(name, cousin)
            self.cousinByKit.setdefault(kit,cousin)


    def importGrandparents(self):
        siblings_df = pd.read_excel('visualphasing.xlsx', sheet_name='Grandparents', header=0, engine='openpyxl')

        for index, row in siblings_df.iterrows():
            name = row['Name'].strip()

            grandparent = Grandparent(name=name)
            self.grandparentsByName.setdefault(name, grandparent)

    def importSiblings(self):
        siblings_df = pd.read_excel('visualphasing.xlsx', sheet_name='Siblings', header=0, engine='openpyxl')

        for index, row in siblings_df.iterrows():
            name = row['Name'].strip()
            kit = row['Kit'].strip()

            sibling = Sibling(name=name, kit=kit)
            self.siblingsByName.setdefault(name, sibling)
            self.siblingsByKit.setdefault(kit, sibling)


    def importSiblingOverlap(self):
        siblings_df = pd.read_excel('visualphasing.xlsx', sheet_name='SiblingOverlaps', header=0, engine='openpyxl')

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
                    siblingOverlap.sibling_keys.append(sibling.kit)

            self.overlaps.append(siblingOverlap)

    def importGrandparentSegments(self):
        siblings_df = pd.read_excel('visualphasing.xlsx', sheet_name='GrandparentSegments', header=0, engine='openpyxl')

        for index, row in siblings_df.iterrows():
            chromosome = row['Chr']
            sibling = row['Sibling']
            kit = "add later"
            grandparent = row['Grandparent']
            start = int(row['B37 Start'])
            end = int(row['B37 End'])
            segment = GrandparentSegment(chromosome, sibling, kit, grandparent, start, end)

            self.grandparent_segments.append(segment)

    def importGrandparentSegments2(self):
        # read the excel file into a pandas dataframe using the openpyxl engine
        df = pd.read_excel('visualphasing.xlsx', sheet_name='GrandparentSegments', header=0, engine='openpyxl')

        # group by the "Chromosome" column and sort each group by "B37 Start" and "B37 End"
        df_grouped = df.groupby('Chromosome').apply(lambda x: x.sort_values(['B37 Start', 'B37 End'])).reset_index(drop=True)

        # enumerate the values of each group using the headers
        for name, group in df_grouped.groupby('Chromosome'):
            print(f"Chromosome {name}:")
            for index, row in group.iterrows():
                print(f"\tRow {index}:")
                for col, val in row.items():
                    print(f"\t\t{col}: {val}")

def exportToCsv(triangs: List[Triang]):
    df = pd.DataFrame([vars(triang) for triang in triangs])

    df.to_csv('matched_triangulations.csv', index=False)
    # with open('matched_triangulations.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(['Name', 'Age', 'Gender'])
    #     for person in people:
    #         writer.writerow([person.name, person.age, person.gender])

@dataclass
class TriagImporter:
    def importCsv(self, directory: str):
        for root, dirs, files in os.walk(self.directory):
            for filename in fnmatch.filter(files, '*.csv'):
                file_path: str = os.path.join(root, filename)
                triang_list = self.createList(file_path)
                print(file_path)
                print(triang_list)

    def createList(self, file_path: str) -> []:
        triang_list = []
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                triang = Triang(row["Chr"], row["Kit1 Number"], row["Kit1 Name"], row["Kit1 Email"], row["Kit2 Number"], row["Kit2 Name"], row["Kit2 Email"], int(row["B37 Start"]), int(row["B37 End"]), row["cM"])
                triang_list.append(triang)
        return triang_list

directory: str = f"C:\\_documents\\personal\\DNA\\visualphasing\\triangulation\\Python"
excelImporter:ExcelImporter = ExcelImporter(directory)
excelImporter.importExcel()

siblingsByKit: Dict[str, Sibling] = excelImporter.siblingsByKit
cousinByKit: Dict[str, Cousin] = excelImporter.cousinByKit

for siblingName in siblingsByKit.keys():
    print('Sibling-' + siblingName)

for cousinName in cousinByKit.keys():
    print('Cousin-' + cousinName)

for grandparentName in excelImporter.grandparentsByName.keys():
    print(grandparentName)

triangulationBySiblingKit: Dict[str, List[Triang]] = {}
triangBySiblingByChr: Dict[str, List[Triang]] = {}
for sibling in excelImporter.siblingsByName.values():
    file_path: str = os.path.join(directory, sibling.kit.strip() + ".csv")
    importer: TriagImporter = TriagImporter()
    triang_list = importer.createList(file_path)
    triangulationBySiblingKit.setdefault(sibling.kit.strip(), triang_list)

    # Create a dictionary where the keys are Chr values and the values are lists of Triang instances with that Chr value

    for triang in triang_list:
        key: str = sibling.kit + '-' + triang.Chr
        if key not in triangBySiblingByChr:
            triangBySiblingByChr[key] = []
        triangBySiblingByChr[key].append(triang)

    print(file_path)
    print(triang_list)

filteredTriang: List[Triang] = []
for overlap in excelImporter.overlaps:

    cousinKitsToExclude: List[int] =[]
    for cuz in cousinByKit.values():
        if overlap.Grandparent == cuz.grandparent:
            pass
        else:
            cousinKitsToExclude.append(cuz.kit)
    

    bestSiblingKit:str = overlap.siblings_list[0].kit
    key: str = bestSiblingKit + '-' + triang.Chr
    chr_triang_list: List[Triang] = triangBySiblingByChr[key]
    sorted_list: List[Triang] = sorted(chr_triang_list, key=lambda t: (t.Kit1_Number, t.B37_Start, t.B37_End))

    currentKit1_NumberTriangList: List[Triang] = []
    currentKit1_Number: str = 0
    siblingKitCountGroup: Dict[str,int] = {}
    groupContainsExcludedCousin: bool = False

    t: Triang
    for t in sorted_list:
        if currentKit1_Number != t.Kit1_Number:

            #Make sure the rows contain at least 1 row for each overlap sibling
            add_group: bool = True
            for overlapSibling in overlap.siblings_list:
                if overlapSibling.kit != bestSiblingKit and overlapSibling.kit not in siblingKitCountGroup.keys():
                    add_group = False
 

            # make sure group does not contain any NON overlap siblings
            for groupSiblingKit in siblingKitCountGroup.keys():
                if groupSiblingKit not in overlap.sibling_keys:
                    add_group = False

    #       If any triang within the Kit1_Number group is one of the "Excluded Cousin Kits", then remove the entire group
            if groupContainsExcludedCousin == True:
                add_group = False

            if currentKit1_Number in cousinKitsToExclude:
                add_group = False

            if currentKit1_Number in siblingsByKit.keys():
                add_group = False

            if add_group == True:
                filteredTriang += currentKit1_NumberTriangList
            #reset all group related symbols
            currentKit1_NumberTriangList = []
            currentKit1_Number = t.Kit1_Number
            siblingKitCountGroup = {}
            groupContainsExcludedCousin = False

        if t.B37_Start >= overlap.B37_Start and t.B37_Start <= overlap.B37_End and t.B37_End <= overlap.B37_End:
            currentKit1_NumberTriangList.append(t)

            if t.Kit2_Number in siblingsByKit:
                if t.Kit2_Number not in siblingKitCountGroup.keys():
                    siblingKitCountGroup[t.Kit2_Number] = 1
                else:
                    siblingKitCountGroup[t.Kit2_Number] +=1
            if t.Kit2_Number in cousinKitsToExclude:
                groupContainsExcludedCousin = True

exportToCsv(filteredTriang)
