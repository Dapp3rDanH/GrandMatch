# GEDmatch Triangulation Input

**Directory:** `inputfiles/gedmatch/triangulation/`

## Purpose

This directory contains GEDmatch "people in common" triangulation exports — one CSV file per sibling. Each file lists pairs of people who both match that sibling on the same DNA segment (i.e., all three share an overlapping segment, forming a triangulation).

These records are the raw material that GrandMatch filters against calculated overlaps to identify potential cousin matches for each grandparent.

## File Naming

Each file must be named `{Kit}.csv`, where `{Kit}` matches the sibling's kit number from the **Siblings** sheet in `visualphasing.xlsx`.

For example, if the Siblings sheet contains:

| Name | Kit |
|------|-----|
| Dale | T806693 |
| Debbie | BA1871856 |

Then the directory must contain:
```
inputfiles/gedmatch/triangulation/T806693.csv
inputfiles/gedmatch/triangulation/BA1871856.csv
```

## Required Columns

| Column | Type | Description |
|--------|------|-------------|
| Chr | string | Chromosome number (1–22, or "X"). "X" is converted to 23 internally. |
| Kit1 Number | string | GEDmatch kit number of the first matching person |
| Kit1 Name | string | Name of Kit1 |
| Kit1 Email | string | Email of Kit1 |
| Kit2 Number | string | GEDmatch kit number of the second matching person |
| Kit2 Name | string | Name of Kit2 |
| Kit2 Email | string | Email of Kit2 |
| B37 Start | integer | Segment start position (Build 37 coordinates) |
| B37 End | integer | Segment end position (Build 37 coordinates) |
| cM | string | Size of the shared segment in centimorgans |

## How This Data Is Used

1. **Loading** (`get_triangulation`): Each sibling's CSV is parsed into a list of `Triang` objects and stored in `triangulationBySiblingKit[kit]`.

2. **Bucketing** (`LoopOnChromosomeData`): Triangulation records are split by chromosome into each `ChromosomeModel.triangBySibling[kit]`.

3. **Matching** (`match_chromosomes`): For each overlap region, the pipeline takes the first sibling's triangulation records, groups them by Kit1 (the potential cousin), and applies filtering rules to determine if Kit1 is a valid cousin candidate for that grandparent.

## Notes

- All position values use **Build 37** (GRCh37/hg19) coordinates.
- The "X" chromosome is supported and mapped to chromosome 23.
- Kit1 and Kit2 in a triangulation row represent two people who both match the sibling (the file owner) on the same segment. Kit1 is treated as the potential cousin; Kit2 is checked to see if it's another sibling.
