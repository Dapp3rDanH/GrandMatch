# GEDmatch Segment Matches Input

**Directory:** `inputfiles/gedmatch/matches/`

## Purpose

This directory contains GEDmatch one-to-one segment match exports. These are direct segment comparisons between a sibling and another person (unlike triangulation, which involves three-way matches).

This data is used in the final step of the pipeline (`extract_kits`) to cross-reference: once the pipeline identifies potential cousins through triangulation matching, it checks this segment match data to find which siblings also have a direct segment match with that cousin on any chromosome.

## File Format

Any `.csv` files in this directory (including subdirectories) are read by `GedMatchSegmentImporter`. There is no required naming convention — all CSVs found are loaded and combined.

## Required Columns

| Column | Type | Description |
|--------|------|-------------|
| PrimaryKit | string | The sibling's GEDmatch kit number |
| MatchedKit | string | The matched person's kit number |
| chr | string | Chromosome number (1–22, or "X"). "X" is converted to 23 internally. |
| B37Start | integer | Segment start position (Build 37 coordinates) |
| B37End | integer | Segment end position (Build 37 coordinates) |
| Segment cM | string | Size of the shared segment in centimorgans |
| SNPs | string | Number of SNPs in the segment |
| MatchedName | string | Name of the matched person |
| Matched Sex | string | Sex of the matched person |
| MatchedEmail | string | Email of the matched person |

## How This Data Is Used

In the `extract_kits` method:

1. The pipeline first builds a `chromosome_matches` dictionary from the filtered triangulation results — one entry per unique (Kit, Chromosome) combination.
2. It then loads all segment match CSVs from this directory.
3. For each chromosome match, it searches the segment data for rows where `MatchedKit` equals the cousin's kit number.
4. Matches are written to `other_matches.csv`, showing which siblings have direct segment matches with the identified cousins.

## Notes

- Column names differ from the triangulation CSVs (e.g. `B37Start` vs `B37 Start`, `PrimaryKit` vs `Kit1 Number`).
- All position values use **Build 37** (GRCh37/hg19) coordinates.
