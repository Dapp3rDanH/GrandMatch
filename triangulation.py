import csv
import os
import fnmatch
from dataclasses import dataclass, field
import pandas as pd
from typing import Dict, List
from enum import Enum

from gedmatch_segment import GedMatchSegment, GedMatchSegmentImporter
from sibling_match import SiblingMatch

# from excel_importer import ExcelImporter

@dataclass
class GrandparentSegment:
    Chr: int
    Sibling: str
    Kit: str
    Grandparent: str  
    B37_Start: int
    B37_End: int

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

@dataclass
class GrandparentTriang(Triang):
    grandparent: str

    
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
class ChromosomeMatch:
    name: str
    kit: str
    grandparent: str
    chr: int

@dataclass
class SiblingOverlap:
    Chr: int
    # Siblings: str
    Grandparent: str  
    B37_Start: int
    B37_End: int
    sibling_kits: List[str] = field(default_factory=list)
    segments: List[GrandparentSegment] = field(default_factory=list)

class MilestoneType(Enum):
    START = 1
    END = 2

@dataclass
class Milestone:
    segment: GrandparentSegment
    milestone_type: MilestoneType
    event_number: int = 0
    is_active: bool = False

@dataclass
class OverlapCalculator:
    segment_list: List[GrandparentSegment]
    # siblingsByName: Dict[str, Sibling] = field(default_factory=dict)
    siblingsByKit: Dict[str, Sibling] = field(default_factory=dict)

    def calculate_overlaps(self):
        non_active_milestones: List[Milestone] = []
        smallest: int = 0
        largest: int = 0
        for segment in self.segment_list:
            non_active_milestones.append(Milestone(segment= segment, milestone_type= MilestoneType.START,  event_number = segment.B37_Start, is_active=False))
            non_active_milestones.append(Milestone(segment= segment, milestone_type= MilestoneType.END,  event_number = segment.B37_End, is_active=False))
            largest = max(segment.B37_End, largest)
            smallest = max(segment.B37_Start, smallest)

        sorted_milestones = sorted(non_active_milestones, key=lambda m: (m.event_number))
        overlaps = []
 
        #determine what segments are active
        activated_segments :List[GrandparentSegment] = []
        active_event_number:int = 0
        while active_event_number < largest:
            for m in sorted_milestones:
                if m.event_number > active_event_number:
                    break
                if m.is_active == False and m.event_number == active_event_number:
                    m.is_active = True
                    activated_segments.append(m.segment)


            overlap_end: int
            #find the first non-activated milestone
            for m in sorted_milestones:
                if m.is_active == False:
                    overlap_end = m.event_number
                    break
            #if this milestone is Type=End, then lets remove the segment after creating overlap
            milestones_to_deactivate : List[segment] = []
            for m in sorted_milestones:
                if m.milestone_type == MilestoneType.END and m.event_number == overlap_end:
                    m.is_active = True
                    milestones_to_deactivate.append(m)

            if len(activated_segments) > 0:
                overlap_start = max(seg.B37_Start for seg in activated_segments)
                overlap_start = max(overlap_start, active_event_number)
                chr = activated_segments[0].Chr
                grandparent = activated_segments[0].Grandparent

                overlap_segments = activated_segments[:]
                sibling_keys : List[str] = []
                for s in overlap_segments:
                    sibling_keys.append(s.Kit)

                overlap: SiblingOverlap = SiblingOverlap(segments=overlap_segments, B37_Start=overlap_start, B37_End=overlap_end, Chr=chr, Grandparent=grandparent, sibling_kits=sibling_keys)
                overlaps.append(overlap)
                #remove any segments where the end milestone were active
                for m in milestones_to_deactivate:
                    for seg in activated_segments:
                        if seg == m.segment:
                            activated_segments.remove(seg)

            active_event_number = overlap_end

        return overlaps

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

@dataclass()
class ChromosomeModel:
    grand_match: "GrandMatch"
    chr: int
    segmentsByGrandparent: Dict[str, List[GrandparentSegment]] = field(default_factory=dict)
    overlapsByGrandparent: Dict[str, List[SiblingOverlap]] = field(default_factory=dict)
    triangBySibling: Dict[str, List[Triang]] = field(default_factory=dict)

    def __post_init__(self):
        pass

@dataclass()
class ChromosomeSetting:
    chr: int
    mode: str = "No"



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
    overlaps : List[SiblingOverlap] = field(default_factory=list)
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


@dataclass()
class GrandMatch:

    siblingsByKit: Dict[str, Sibling] = field(default_factory=dict)
    cousinByKit: Dict[str, Cousin] = field(default_factory=list)
    chromosome_models: Dict[int, ChromosomeModel] = field(default_factory=dict)
    siblingsByName: Dict[str, Sibling] = field(default_factory=dict)

    grandparentsByName: Dict[str, Grandparent] = field(default_factory=dict)
    grandparentsByKit: Dict[str, Grandparent] = field(default_factory=dict)
    cousinByName: Dict[str, Cousin] = field(default_factory=dict)
    cousinByKit: Dict[str, Cousin] = field(default_factory=dict)
    grandparent_segments: List[GrandparentSegment] = field(default_factory=list)
    overlaps : List[SiblingOverlap] = field(default_factory=list)
    sibling_overlap_by_chr: Dict[str, SiblingOverlap] = field(default_factory=dict)
    triangulationBySiblingKit: Dict[str, List[Triang]] = field(default_factory=dict)


    def print(self):
        for siblingName in self.siblingsByKit.keys():
            print('Sibling-' + siblingName)

        for cousinName in self.cousinByKit.keys():
            print('Cousin-' + cousinName)

        for grandparentName in self.grandparentsByName.keys():
            print(grandparentName)

        for chr in self.sibling_overlap_by_chr.keys():
            overlaps = self.sibling_overlap_by_chr[chr]
            for overlap in overlaps:
                print(f"Chr {chr} SiblingOverlap from {overlap.B37_Start} to {overlap.B37_End} between segments:")
                for seg in overlap.segments:
                    print(f"  - {seg.Sibling} ({seg.B37_Start} to {seg.B37_End})")

    def create_chromosome_models(self, chromosome_settings_by_chr: Dict[int, ChromosomeSetting]):

        #separate the grandpatnet segments by chromosome.
        for segment in self.grandparent_segments:
            # get the chromosome name
            chr_number = segment.Chr
            if chromosome_settings_by_chr[chr_number].mode == "Yes":
                # if the chromosome name is not already a key in the dictionary, add it with an empty list as the value
                if chr_number not in self.chromosome_models:
                    self.chromosome_models[chr_number] = ChromosomeModel(chr=chr_number,grand_match=self)

                chromosome_model = self.chromosome_models[chr_number]
                if segment.Grandparent not in chromosome_model.segmentsByGrandparent:
                    chromosome_model.segmentsByGrandparent[segment.Grandparent] = []
                chromosome_model.segmentsByGrandparent[segment.Grandparent].append(segment)

    def LoopOnChromosomeData(self):
        for chr_number in self.chromosome_models.keys():
            chromosome_model: ChromosomeModel = self.chromosome_models[chr_number]
            for grandparent in chromosome_model.segmentsByGrandparent.keys():
                segments = chromosome_model.segmentsByGrandparent[grandparent]
                calculator = OverlapCalculator(segments,self.siblingsByKit)
                overlaps = calculator.calculate_overlaps()
                chromosome_model.overlapsByGrandparent[grandparent] = overlaps


            for sibling_kit in self.siblingsByKit.keys():
            #         file_path: str = os.path.join(directory, sibling.kit.strip() + ".csv")
            #         importer: TriagImporter = TriagImporter()
            #         triang_list = importer.createList(file_path)
                    sibling_triangulation = self.triangulationBySiblingKit[sibling_kit]

                    # Create a dictionary for this sibling for just this chromosome
                    for triang in sibling_triangulation:
                        if triang.Chr == chr_number:
                            if sibling_kit not in chromosome_model.triangBySibling:
                                chromosome_model.triangBySibling[sibling_kit] = []
                            chromosome_model.triangBySibling[sibling_kit].append(triang)


    def match_chromosomes(self) -> List[Triang]:
        filteredTriang: List[Triang] = []
        for chr_number in self.chromosome_models.keys():
            chrome: ChromosomeModel = self.chromosome_models[chr_number]
            for gparent in self.grandparentsByName.keys():

                if gparent in chrome.overlapsByGrandparent:
                    overlaps = chrome.overlapsByGrandparent[gparent]

                    cousinKitsToExclude: List[int] =[]
                    for cuz in self.cousinByKit.values():
                        if gparent == cuz.grandparent:
                            pass
                        else:
                            cousinKitsToExclude.append(cuz.kit)


                    overlap:SiblingOverlap
                    for overlap in overlaps:

                        bestSiblingKit:str = overlap.sibling_kits[0]
                        chr_triang_list: List[Triang] = chrome.triangBySibling[bestSiblingKit]
                        sorted_list: List[Triang] = sorted(chr_triang_list, key=lambda t: (t.Kit1_Number, t.B37_Start, t.B37_End))

                        triangGroup = TriangGroup() 
                        t: Triang
                        for t in sorted_list:
                            if triangGroup.kit_Number != t.Kit1_Number:
                                #Make sure the rows contain at least 1 row for each overlap sibling
                                add_group: bool = True
                                for overlapSiblingKit in overlap.sibling_kits:
                                    if overlapSiblingKit != bestSiblingKit and overlapSiblingKit not in triangGroup.siblingKitCountGroup.keys():
                                        add_group = False
                    
                                # make sure group does not contain any NON overlap siblings
                                for groupSiblingKit in triangGroup.siblingKitCountGroup.keys():
                                    if groupSiblingKit not in overlap.sibling_kits:
                                        add_group = False

                        #       If any triang within the Kit1_Number group is one of the "Excluded Cousin Kits", then remove the entire group
                                if triangGroup.groupContainsExcludedCousin == True:
                                    add_group = False

                                if triangGroup.kit_Number in cousinKitsToExclude:
                                    add_group = False

                                if triangGroup.kit_Number in self.siblingsByKit.keys():
                                    add_group = False

                                if add_group == True:
                                    if len(triangGroup.triang_list)>0:
                                        # for t in triangGroup.triang_list:
                                            # if t.Chr == 2:
                                            #     print(t.Chr)
                                        filteredTriang += triangGroup.triang_list

                                # print((filteredTriang))

                                triangGroup.reset(t.Kit1_Number, t.Chr)

                            if t.B37_Start >= overlap.B37_Start and t.B37_Start <= overlap.B37_End and t.B37_End <= overlap.B37_End:
                                t.grandparent = gparent
                                t.source_sibling = bestSiblingKit
                                # if t.Chr == 2:
                                #     print(t.Chr)
                                triangGroup.triang_list.append(t)

                                # if kit2 is one of the siblings
                                if t.Kit2_Number in self.siblingsByKit:
                                    #if kit2 has not already been added to group
                                    if t.Kit2_Number not in triangGroup.siblingKitCountGroup.keys():
                                        triangGroup.siblingKitCountGroup[t.Kit2_Number] = 1
                                    else:
                                        triangGroup.siblingKitCountGroup[t.Kit2_Number] +=1
                                if t.Kit2_Number in cousinKitsToExclude:
                                    triangGroup.groupContainsExcludedCousin = True
        return filteredTriang


    def get_triangulation(self):
        for sibling in self.siblingsByName.values():
            file_path: str = os.path.join(directory, sibling.kit.strip() + ".csv")
            importer: TriagImporter = TriagImporter()
            triang_list = importer.createList(file_path)
            self.triangulationBySiblingKit.setdefault(sibling.kit.strip(), triang_list)

    def export_overlaps(self):
        for sibling_kit in self.siblingsByKit.keys():
                sibling_triangulation = self.triangulationBySiblingKit[sibling_kit]
                df = pd.DataFrame([vars(o) for o in sibling_triangulation])
                df.to_csv(f'out\\triangs-{sibling_kit}.csv', index=False)

        all_overlaps = []
        for chr_number in self.chromosome_models.keys():
            chrome: ChromosomeModel = self.chromosome_models[chr_number]
            for gparent in self.grandparentsByName.keys():

                if gparent in chrome.overlapsByGrandparent:
                    overlaps = chrome.overlapsByGrandparent[gparent]
                    all_overlaps.extend(overlaps)
                    df = pd.DataFrame([vars(o) for o in overlaps])
                    # drop the 'segments' column
                    df = df.drop('segments', axis=1)
                    df.to_csv(f'out\\overlaps-{chr_number}-{gparent}.csv', index=False)

                    segments = chrome.segmentsByGrandparent[gparent]
                    df = pd.DataFrame([vars(o) for o in segments])
                    df.to_csv(f'out\\segments-{chr_number}-{gparent}.csv', index=False)

            for sibling_kit in self.siblingsByKit:
                    triangs = chrome.triangBySibling[sibling_kit]
                    df = pd.DataFrame([vars(o) for o in triangs])
                    df.to_csv(f'out\\triangs-{chr_number}-{sibling_kit}.csv', index=False)

        df = pd.DataFrame([vars(o) for o in all_overlaps])
        # drop the 'segments' column
        df = df.drop('segments', axis=1)
        df.to_csv(f'out\\all_overlaps.csv', index=False)

    def make_out_folder(self, directory: str):
        # Check if the directory already exists
        if not os.path.exists(directory):
            # Create the directory
            os.makedirs(directory)
            print(f"Directory '{directory}' created successfully!")
        else:
            print(f"Directory '{directory}' already exists.")

    def export_triangs_to_csv(self, triangs: List[Triang]):
        directory = "out"
        self.make_out_folder(directory)
        df = pd.DataFrame([vars(triang) for triang in triangs])
        df.to_csv(f'{directory}\\matched_triangulations.csv', index=False)

    def export_chromosome_matches_to_csv(self, chromosome_matches: List[ChromosomeMatch]):
        directory: str = "out"
        self.make_out_folder(directory)
        df = pd.DataFrame([vars(c) for c in chromosome_matches])
        df.to_csv(f'{directory}\\chromosome_matches.csv', index=False)
    
    def extract_kits(self, triangs: List[Triang]):
        matchesByKit: Dict[(str, int), List[ChromosomeMatch]] = {}
        for t in triangs:
            key = (t.Kit1_Number, t.Chr)
            if key not in matchesByKit:
                matchesByKit[key] = ChromosomeMatch(name=t.Kit1_Name,kit=t.Kit1_Number, grandparent=t.grandparent, chr=t.Chr)

        self.export_chromosome_matches_to_csv(matchesByKit.values())

        gedmatch_importer = GedMatchSegmentImporter()
        segment_list: List[GedMatchSegment] = gedmatch_importer.importCsv(directory=os.getcwd() + "\\inputfiles\\gedmatch")

        other_matches: Dict[str, SiblingMatch] = {}
        for kit_chr in matchesByKit.keys():
            for s in segment_list:
                if kit_chr[0] == s.matched_kit:
                    key = (s.matched_kit, s.chromosome)
                    if key not in other_matches:
                        sibling_match = SiblingMatch(chr=s.chromosome, cousin_kit=s.matched_kit, cousin_name=s.matched_name, sibling_kit=s.primary_kit, sibling_name=s.primary_kit)
                        other_matches[key] = sibling_match

        df = pd.DataFrame([vars(c) for c in other_matches.values()])
        df.to_csv(f'out\\other_matches.csv', index=False)
            
                



directory = os.getcwd() + "\\inputfiles"
# Set the file name
file_name = "visualphasing.xlsx"
# Join the working directory and file name to create the full path
full_path = os.path.join(directory, file_name)

excelImporter:ExcelImporter = ExcelImporter(full_path)
excelImporter.importExcel()

grandMatch = GrandMatch()
grandMatch.siblingsByKit = excelImporter.siblingsByKit
grandMatch.siblingsByName = excelImporter.siblingsByName

grandMatch.grandparentsByKit = excelImporter.grandparentsByKit
grandMatch.grandparentsByName = excelImporter.grandparentsByName

grandMatch.cousinByName = excelImporter.cousinByName
grandMatch.cousinByKit = excelImporter.cousinByKit

grandMatch.grandparent_segments = excelImporter.grandparent_segments

grandMatch.overlaps = excelImporter.overlaps

grandMatch.get_triangulation()
grandMatch.print()

grandMatch.create_chromosome_models(excelImporter.chromosome_settings_by_chr)
# grandMatch.create_overlap_by_chr()
grandMatch.LoopOnChromosomeData()
filteredTriang = grandMatch.match_chromosomes()
# filteredTriang = grandMatch.create_matches()
grandMatch.export_triangs_to_csv(filteredTriang)
grandMatch.extract_kits(filteredTriang)
grandMatch.export_overlaps()



