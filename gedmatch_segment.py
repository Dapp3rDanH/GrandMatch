from dataclasses import dataclass
import csv
import os
import fnmatch
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from triangulation import Triang

@dataclass
class GedMatchSegment:
    primary_kit: str
    matched_kit: str
    chromosome: int
    b37_start: str
    b37_end: str
    segment_cm: str
    snps: str
    matched_name: str
    matched_sex: str
    matched_email: str


@dataclass
class GedMatchSegmentImporter:
    def importCsv(self, directory: str)-> List[GedMatchSegment]:
        segment_list: List[GedMatchSegment] = []
        for root, dirs, files in os.walk(directory):
            for filename in fnmatch.filter(files, '*.csv'):
                file_path: str = os.path.join(root, filename)
                sibling_segments = self.createList(file_path)
                segment_list.extend(sibling_segments)
                # print(file_path)
                # print(triang_list)
        return segment_list

    def createList(self, file_path: str) -> List[GedMatchSegment]:
        segment_list = []
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                PrimaryKit = row["PrimaryKit"]
                MatchedKit	= row["MatchedKit"]
                chr	= row["chr"]
                if chr == "X":
                    chr = 23
                B37Start	= row["B37Start"]
                B37End	= row["B37End"]
                Segment = row["Segment cM"]
                SNPs	= row["SNPs"]
                MatchedName	= row["MatchedName"]
                matched_sex = row["Matched Sex"]
                MatchedEmail= row["MatchedEmail"]

                segment = GedMatchSegment(b37_end=B37End, b37_start=B37Start, chromosome=int(chr), matched_email=MatchedEmail, matched_kit=MatchedKit, matched_name=MatchedName, matched_sex=matched_sex, snps=SNPs, segment_cm=Segment, primary_kit=PrimaryKit)
                segment_list.append(segment)
        return segment_list