# Pipeline Overview

## The Big Idea

GrandMatch combines two sources of genetic information:

1. **Visual phasing results** — Manual analysis that determines which DNA segments each sibling inherited from which grandparent. This is configured in `visualphasing.xlsx`.

2. **GEDmatch triangulation data** — Automated exports showing which unknown people triangulate (share overlapping DNA segments) with your siblings.

The tool asks: *"Given the regions where multiple siblings inherited DNA from the same grandparent, which unknown people triangulate with the right combination of siblings in those regions?"*

The output is a list of candidate cousin matches, each tagged with the grandparent they likely descend from.

## Pipeline Steps

The pipeline is orchestrated by `main_grand_match.py` and the `GrandMatch` class.

### Step 1: Import Excel Configuration

**Code:** `ExcelImporter.importExcel()` → populates `GrandMatch` fields

Reads `inputfiles/visualphasing.xlsx` and creates domain objects:
- Siblings (by name and kit)
- Cousins (by name and kit, each tagged with a grandparent)
- Grandparents (by name)
- Grandparent segments (the visual phasing assignments)
- Chromosome settings (which chromosomes to analyze)

### Step 2: Load Triangulation Data

**Code:** `GrandMatch.get_triangulation(directory)`

For each sibling, reads `inputfiles/gedmatch/triangulation/{kit}.csv` via `TriagImporter`. Each row becomes a `Triang` object representing a three-way match: the sibling, Kit1, and Kit2 all share an overlapping DNA segment.

Results are stored in `triangulationBySiblingKit[kit]`.

### Step 3: Create Chromosome Models

**Code:** `GrandMatch.create_chromosome_models(chromosome_settings)`

Groups grandparent segments by chromosome number. Only chromosomes with `Mode = "Yes"` in the chromosomes sheet are included. Each enabled chromosome gets a `ChromosomeModel` that organizes segments by grandparent.

### Step 4: Calculate Overlaps and Bucket Triangulations

**Code:** `GrandMatch.LoopOnChromosomeData()`

For each chromosome, two things happen:

**4a — Overlap Calculation:** For each grandparent's segments on this chromosome, `OverlapCalculator` finds where multiple siblings inherited from the same grandparent on overlapping DNA ranges. These overlaps are the regions where triangulation is meaningful — if two siblings both got DNA from Grandpa Smith at positions 50M–80M, then anyone triangulating with both siblings in that range is likely a Smith cousin.

The algorithm works by:
1. Creating START and END milestone events for each segment
2. Sorting milestones by position
3. Walking through positions, tracking which segments are "active"
4. Emitting a `SiblingOverlap` wherever 1+ segments overlap, recording which sibling kits are involved

**4b — Triangulation Bucketing:** Each sibling's triangulation records are also sliced into the per-chromosome model for efficient lookup in the next step.

### Step 5: Match Triangulations to Overlaps

**Code:** `GrandMatch.match_chromosomes()`

This is the core matching logic. For each overlap region on each chromosome for each grandparent:

1. **Pick a sibling** — Take the first sibling kit from the overlap (`bestSiblingKit`).
2. **Get triangulations** — Retrieve that sibling's triangulation records for this chromosome, sorted by Kit1 (the potential cousin).
3. **Group by Kit1** — Process triangulations in groups where Kit1 is the same person. Each group is a `TriangGroup`.
4. **Filter each group** — A group is excluded if:
   - Kit1 is itself a sibling (not a cousin)
   - Kit1 is a known cousin assigned to a **different** grandparent
   - The group contains a triangulation with a cousin from a different grandparent (via Kit2)
   - The group does **not** contain triangulations with **all** other siblings in the overlap
   - The group contains triangulations with siblings who are **not** in the overlap
5. **Tag survivors** — Triangulation records that pass all filters are tagged with the grandparent name and source sibling kit.

### Step 6: Export Results

**Code:** `export_triangs_to_csv()`, `extract_kits()`, `export_overlaps()`

Three export operations write CSV files to `out/{timestamp}/`:
- **Matched triangulations** — The filtered results from Step 5
- **Chromosome matches + other matches** — Deduplicated matches cross-referenced against GEDmatch segment match data (from `inputfiles/gedmatch/matches/`)
- **Overlaps, segments, and raw triangulations** — Per-chromosome/grandparent breakdowns for inspection

See [040_output-files.md](040_output-files.md) for details on each output file.

## Data Flow Diagram

```
visualphasing.xlsx
    ├── Siblings ──────────────┐
    ├── Cousins ───────────────┤
    ├── Grandparents ──────────┤
    ├── GrandparentSegments ───┤
    └── chromosomes ───────────┤
                               ▼
                         GrandMatch
                               │
  triangulation/*.csv ────────►├── ChromosomeModels (per enabled chr)
                               │     ├── segmentsByGrandparent
                               │     ├── overlapsByGrandparent  ◄── OverlapCalculator
                               │     └── triangBySibling
                               │
                               ▼
                      match_chromosomes()
                               │
                               ▼
                      Filtered Triang list
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                     ▼
  matched_triangulations   chromosome_matches   per-chr/grandparent
       .csv                + other_matches.csv   overlap & segment CSVs
```
