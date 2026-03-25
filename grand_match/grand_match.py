from dataclasses import dataclass, field
import os
from typing import Dict, List

from grand_match import Sibling, Cousin, Grandparent, ChromosomeModel, GrandparentSegment, SiblingOverlap
from grand_match import Triang, ChromosomeSetting, OverlapCalculator, TriangGroup, TriagImporter, ChromosomeMatch
from grand_match import GedMatchSegmentImporter, GedMatchSegment, SiblingMatch
import pandas as pd

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

        #separate the grandparent segments by chromosome.
        for segment in self.grandparent_segments:
            # get the chromosome name
            chr_number = segment.Chr
            if chromosome_settings_by_chr[chr_number].mode.lower() == "yes":
                # if the chromosome is not already a key in the dictionary, add it with an empty list as the value
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


    def get_triangulation(self, directory: str):
        for sibling in self.siblingsByName.values():
            file_path: str = os.path.join(directory, sibling.kit.strip() + ".csv")
            importer: TriagImporter = TriagImporter()
            triang_list = importer.createList(file_path)
            self.triangulationBySiblingKit.setdefault(sibling.kit.strip(), triang_list)

    def export_overlaps(self, directory: str):
        for sibling_kit in self.siblingsByKit.keys():
                sibling_triangulation = self.triangulationBySiblingKit[sibling_kit]
                df = pd.DataFrame([vars(o) for o in sibling_triangulation])
                out_directory = directory + f"\\triangs-{sibling_kit}.csv"
                df.to_csv(out_directory, index=False)

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
                    out_directory = directory + f"\\overlaps-{chr_number}-{gparent}.csv"
                    df.to_csv(out_directory, index=False)

                    segments = chrome.segmentsByGrandparent[gparent]
                    df = pd.DataFrame([vars(o) for o in segments])
                    out_directory = directory + f"\\segments-{chr_number}-{gparent}.csv"
                    df.to_csv(out_directory, index=False)

            for sibling_kit in self.siblingsByKit:
                    triangs = chrome.triangBySibling[sibling_kit]
                    df = pd.DataFrame([vars(o) for o in triangs])
                    out_directory = directory + f"\\triangs-{chr_number}-{sibling_kit}.csv"
                    df.to_csv(out_directory, index=False)

        df = pd.DataFrame([vars(o) for o in all_overlaps])
        # drop the 'segments' column
        # df = df.drop('segments', axis=1)
        out_directory = directory + f"\\all_overlaps.csv"
        df.to_csv(out_directory, index=False)

    def make_out_folder(self, directory: str):
        # Check if the directory already exists
        if not os.path.exists(directory):
            # Create the directory
            os.makedirs(directory)
            print(f"Directory '{directory}' created successfully!")
        else:
            print(f"Directory '{directory}' already exists.")

    def export_triangs_to_csv(self, triangs: List[Triang], directory: str):

        self.make_out_folder(directory)
        df = pd.DataFrame([vars(triang) for triang in triangs])
        df.to_csv(f'{directory}\\matched_triangulations.csv', index=False)

    def export_chromosome_matches_to_csv(self, chromosome_matches: List[ChromosomeMatch]):
        directory: str = "out"
        self.make_out_folder(directory)
        df = pd.DataFrame([vars(c) for c in chromosome_matches])
        df.to_csv(f'{directory}\\chromosome_matches.csv', index=False)
    
    def extract_kits(self, triangs: List[Triang], directory: str):
        matchesByKit: Dict[(str, int), List[ChromosomeMatch]] = {}
        for t in triangs:
            key = (t.Kit1_Number, t.Chr)
            if key not in matchesByKit:
                matchesByKit[key] = ChromosomeMatch(name=t.Kit1_Name,kit=t.Kit1_Number, grandparent=t.grandparent, chr=t.Chr)

        self.export_chromosome_matches_to_csv(matchesByKit.values())

        gedmatch_importer = GedMatchSegmentImporter()
        segment_list: List[GedMatchSegment] = gedmatch_importer.importCsv(directory=os.getcwd() + "\\inputfiles\\gedmatch\\matches")

        other_matches: Dict[str, SiblingMatch] = {}
        for kit_chr in matchesByKit.keys():
            for s in segment_list:
                if kit_chr[0] == s.matched_kit:
                    key = (s.matched_kit, s.chromosome)
                    if key not in other_matches:
                        sibling_match = SiblingMatch(chr=s.chromosome, cousin_kit=s.matched_kit, cousin_name=s.matched_name, sibling_kit=s.primary_kit, sibling_name=s.primary_kit)
                        other_matches[key] = sibling_match

        df = pd.DataFrame([vars(c) for c in other_matches.values()])
        df.to_csv(directory + f'\\other_matches.csv', index=False)
            