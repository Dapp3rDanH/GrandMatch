# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GrandMatch is a Python CLI tool for DNA genealogy analysis. It processes triangulation data from multiple siblings to identify DNA cousins matching at grandparent-level segments. Input is Excel-based configuration + CSV triangulation files; output is timestamped CSV reports.

## Commands

```bash
# Setup
python -m venv venv
venv/Scripts/activate        # Windows
pip install -r requirements.txt

# Run main analysis pipeline
python main_grand_match.py

# Run overlap calculator demo
python main_overlap.py
```

No test suite, linter, or build system is configured.

## Architecture

**Pipeline flow:** Excel config → Domain models → Chromosome models → Overlap calculation → Triangulation matching → CSV export

### Key components in `grand_match/`:

- **`grand_match.py`** — Central orchestrator. Imports config, creates chromosome models, calculates overlaps, matches triangulations, exports CSVs. Methods flow: `importExcel()` → `get_triangulation()` → `create_chromosome_models()` → `LoopOnChromosomeData()` → `match_chromosomes()`
- **`excel_importer.py`** — Reads `inputfiles/visualphasing.xlsx` (sheets: Siblings, Cousins, Grandparents, chromosomes, GrandparentSegments) into domain models
- **`triang_importer.py`** — Reads sibling triangulation CSVs from `inputfiles/gedmatch/triangulation/`
- **`ged_match_segment_importer.py`** — Reads GedMatch segment CSVs
- **`overlap_calculator.py`** — Sweep-line algorithm using START/END milestones to detect overlapping DNA segments across siblings

### Models (`grand_match/models/`):

18 dataclass files. Core: `Sibling`, `Cousin`, `Grandparent`, `GrandparentSegment`, `Triang`, `ChromosomeModel`, `ChromosomeSetting`, `SiblingOverlap`, `Milestone` (with `MilestoneType` enum).

### Entry points:

- **`main_grand_match.py`** — Primary. Full analysis pipeline.
- **`main_overlap.py`** — Demo of OverlapCalculator with hardcoded segments.
- **`main.py`** — Legacy prototype.

## Input/Output

- **Config:** `inputfiles/visualphasing.xlsx` — Excel workbook defining siblings (name/kit), cousins (name/kit/grandparent), grandparents, grandparent segments (chr/sibling/kit/start/end), and chromosome enable/disable settings
- **Triangulation data:** `inputfiles/gedmatch/triangulation/*.csv`
- **Output:** `out/{timestamp}/` with CSVs (matched_triangulations, chromosome_matches, overlaps, segments, etc.)

## Dependencies

pandas, openpyxl, numpy (pinned versions in `requirements.txt`). No external APIs or databases.

## Known Issues

- Windows-specific backslash paths hardcoded in some places (not portable)
- Legacy/unused files exist: `excel_importer_old.py`, `overlap_calculatorOld.py`, `milestone_old.py`
- `__init__.py` references some deleted root-level files
