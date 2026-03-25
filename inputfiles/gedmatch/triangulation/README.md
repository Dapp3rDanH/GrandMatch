# Triangulation Input Files

This directory contains GEDmatch "people in common" triangulation CSV exports — one file per sibling. These files contain personal DNA data and are not tracked in git.

## File Naming

Each file must be named `{Kit}.csv`, where `{Kit}` matches the sibling's kit number from the **Siblings** sheet in `visualphasing.xlsx`.

Example:
```
T806693.csv
BA1871856.csv
```

## Required Columns

| Column | Type | Description |
|--------|------|-------------|
| Chr | string | Chromosome number (1–22, or "X") |
| Kit1 Number | string | Kit number of the first matching person |
| Kit1 Name | string | Name of Kit1 |
| Kit1 Email | string | Email of Kit1 |
| Kit2 Number | string | Kit number of the second matching person |
| Kit2 Name | string | Name of Kit2 |
| Kit2 Email | string | Email of Kit2 |
| B37 Start | integer | Segment start position (Build 37) |
| B37 End | integer | Segment end position (Build 37) |
| cM | string | Segment size in centimorgans |

See [docs/020_gedmatch-triangulation.md](../../../docs/020_gedmatch-triangulation.md) for full details.
