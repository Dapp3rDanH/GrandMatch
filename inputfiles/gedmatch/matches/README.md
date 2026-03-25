# GEDmatch Segment Match Files

This directory contains GEDmatch one-to-one segment match CSV exports. These files contain personal DNA data and are not tracked in git.

All `.csv` files in this directory (including subdirectories) are loaded by the pipeline.

## Required Columns

| Column | Type | Description |
|--------|------|-------------|
| PrimaryKit | string | The sibling's kit number |
| MatchedKit | string | The matched person's kit number |
| chr | string | Chromosome number (1–22, or "X") |
| B37Start | integer | Segment start position (Build 37) |
| B37End | integer | Segment end position (Build 37) |
| Segment cM | string | Segment size in centimorgans |
| SNPs | string | Number of SNPs in the segment |
| MatchedName | string | Name of the matched person |
| Matched Sex | string | Sex of the matched person |
| MatchedEmail | string | Email of the matched person |

See [docs/030_gedmatch-matches.md](../../../docs/030_gedmatch-matches.md) for full details.
