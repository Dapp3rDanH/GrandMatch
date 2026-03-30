# Grid Phasing Tool

Fills the Visual Phaser grandparent grid with PP/PM/M1/M2 labels using a two-phase approach:

1. **Phase 1 (Structural)**: Assigns P1/P2 and M1/M2 using sibling pairwise FIR/HIR/NIR data
2. **Phase 2 (Labeling)**: Maps P1/P2 to PP/PM using cousin data (Amy, Mickey, etc.)

See [phasing_algorithm.md](phasing_algorithm.md) for the full algorithm documentation.

## Usage

Run from the `grid_phasing/` directory:

```bash
cd visual_phaser/grid_phasing
```

### Single chromosome

```bash
python fill_grandparent_grid.py 9
```

### Multiple chromosomes

```bash
python fill_grandparent_grid.py 1 2 3
```

### All chromosomes

```bash
python fill_grandparent_grid.py all
```

### With trace log

Add `--log` to generate a detailed decision trace in `out/logs/`:

```bash
python fill_grandparent_grid.py 9 --log
```

## Input / Output

| File | Location |
|------|----------|
| Input | `../Hickman.xlsx` (never modified) |
| Output | `out/Hickman_phased.xlsx` |
| Trace logs | `out/logs/chr{N}_decisions.md` |

## Export GrandparentSegments CSV

After phasing, export the grid to CSV format compatible with GrandMatch:

```bash
python export_segments.py
```

Or specify a custom input file:

```bash
python export_segments.py path/to/phased_file.xlsx
```

Output: `out/grandparent_segments.csv` with headers `Chr,Sibling,Kit,Grandparent,B37 Start,B37 End`

Copy and paste the CSV contents into the `GrandparentSegments` sheet of `inputfiles/visualphasing.xlsx` before running GrandMatch.

---

## Configuration

Edit the top of `fill_grandparent_grid.py` to configure:

### Cousins

```python
COUSINS = [
    {"name": "Mickey", "grandparent": "M?"},  # maternal, unknown which
    {"name": "Amy",    "grandparent": "PM"},   # paternal-maternal (Bromley)
]
```

Grandparent affiliations: `"PP"`, `"PM"`, `"P?"`, `"MP"`, `"MM"`, `"M?"`

### RP Overrides

Manually remove known-bad recombination points detected by VP auto-detection:

```python
RP_OVERRIDES = {
    9: {
        "Joyce": {"remove": [2]},  # Remove RP at col J (index 2) — noise
    },
}
```

Column indices are 0-based (H=0, I=1, J=2, K=3, ...).
