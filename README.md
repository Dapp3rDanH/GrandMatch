# GrandMatch

Takes DNA triangulation data from multiple siblings and finds DNA cousins that match those siblings at various grandparent segment data.

## Setup

```bash
python -m venv venv
venv/Scripts/activate        # Windows
pip install -r requirements.txt
```

## Running the pipeline

```bash
python main_grand_match.py
```

This runs the full analysis pipeline:

1. Imports configuration from `inputfiles/visualphasing2026.xlsx`
2. Loads triangulation CSVs from `inputfiles/gedmatch/triangulation/`
3. Creates chromosome models and calculates sibling overlaps
4. Matches triangulations against overlaps to identify cousin candidates
5. Exports results to `out/{timestamp}/`

### Configuration

Edit these values at the top of `main_grand_match.py` to change inputs:

| Variable | Default | Description |
|----------|---------|-------------|
| `file_name` | `visualphasing2026.xlsx` | Excel config file in `inputfiles/` |
| `input_triangulation_directory` | `inputfiles/gedmatch/triangulation` | Folder with per-sibling triangulation CSVs |

Enable or disable chromosomes in the `chromosomes` sheet of the Excel file (set Mode to `Yes` or `No`). Only enabled chromosomes are processed.

### Output files

Results are written to `out/{timestamp}/`:

| File | Description |
|------|-------------|
| `matched_triangulations.csv` | All triangulation records that passed matching filters |
| `chromosome_matches.csv` | Deduplicated: one row per (cousin, chromosome, grandparent) |
| `other_matches.csv` | Cross-reference showing which siblings have direct segment matches with identified cousins |
| `overlaps-{chr}-{grandparent}.csv` | Calculated overlap regions per chromosome/grandparent |
| `segments-{chr}-{grandparent}.csv` | Input grandparent segments per chromosome/grandparent |

See `docs/` for detailed documentation on the pipeline, input formats, and output files.
