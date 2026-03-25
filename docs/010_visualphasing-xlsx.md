# visualphasing.xlsx — Configuration Reference

The file `inputfiles/visualphasing.xlsx` is the primary configuration file for GrandMatch. It defines who the siblings and cousins are, which grandparents are being mapped, and the visual phasing segment assignments. It is read by `ExcelImporter` at the start of every pipeline run.

> **Note:** The `inputfiles/` directory also contains `HickmanSiblingsVisualPhase_*.xlsm` files — these are the source visual phasing workbooks (versioned backups and autosave copies). They contain personal DNA data and are excluded from git via `.gitignore`. The `.xlsx` config file is derived from this workbook.

---

## Sheets

### Siblings (required)

Defines the siblings whose DNA is being analyzed.

| Column | Type | Description |
|--------|------|-------------|
| Name | string | Sibling's name (e.g. "Dale") |
| Kit | string | GEDmatch kit number (e.g. "T806693") |

Each sibling must have a corresponding triangulation CSV file at `inputfiles/gedmatch/triangulation/{Kit}.csv`.

---

### Cousins (required)

Lists known cousin matches, each tagged with the grandparent they descend from. Cousins are used during match filtering — a cousin assigned to one grandparent is excluded from matches attributed to a different grandparent.

| Column | Type | Description |
|--------|------|-------------|
| Name | string | Cousin's name |
| Kit | string | GEDmatch kit number |
| Grandparent | string | Name of the grandparent this cousin descends from (must match a value in the Grandparents sheet) |

---

### Grandparents (required)

Lists the grandparents being mapped. Typically 4 (two paternal, two maternal).

| Column | Type | Description |
|--------|------|-------------|
| Name | string | Grandparent identifier (e.g. "Hickman", "Ward") |

---

### GrandparentSegments (required)

The visual phasing results. Each row records a DNA range that a specific sibling inherited from a specific grandparent on a given chromosome.

| Column | Type | Description |
|--------|------|-------------|
| Chr | integer | Chromosome number (1–22) |
| Sibling | string | Sibling name |
| Kit | string | Sibling's GEDmatch kit number |
| Grandparent | string | Grandparent name (must match a value in the Grandparents sheet) |
| B37 Start | integer | Segment start position (Build 37 coordinates) |
| B37 End | integer | Segment end position (Build 37 coordinates) |

These segments are grouped by chromosome and grandparent, then fed into the overlap calculator to find regions where multiple siblings share DNA from the same grandparent.

---

### chromosomes (required)

Controls which chromosomes are included in the analysis.

| Column | Type | Description |
|--------|------|-------------|
| Chr | integer | Chromosome number |
| Mode | string | `"Yes"` to include, `"No"` to skip (case-insensitive) |

Only chromosomes with Mode = "Yes" will have chromosome models created and processed.

---

### SiblingOverlaps (legacy, not required)

Pre-defined sibling overlap regions. This sheet is **not used** by the current pipeline — `importSiblingOverlap()` exists in `ExcelImporter` but is never called from `importExcel()`. The pipeline now calculates overlaps dynamically using `OverlapCalculator`.

| Column | Type | Description |
|--------|------|-------------|
| Chr | integer | Chromosome number |
| Siblings | string | Pipe-delimited sibling names (e.g. "Dale\|Debbie") |
| Grandparent | string | Grandparent name |
| B37 Start | integer | Overlap start position |
| B37 End | integer | Overlap end position |
