from dataclasses import dataclass


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