# Output Files

All output files are written to `out/{timestamp}/`, where `{timestamp}` is a Unix timestamp generated at runtime. Each run creates a new directory.

## Primary Results

### matched_triangulations.csv

The main output. Contains all triangulation records that passed the matching filters in `match_chromosomes()`. Each row is a `Triang` record that was found within an overlap region and satisfied all sibling/cousin validation rules.

| Column | Description |
|--------|-------------|
| Chr | Chromosome number |
| Kit1_Number | Kit number of the potential cousin |
| Kit1_Name | Name of the potential cousin |
| Kit1_Email | Email of the potential cousin |
| Kit2_Number | Kit number of the second person in the triangulation |
| Kit2_Name | Name of Kit2 |
| Kit2_Email | Email of Kit2 |
| B37_Start | Segment start position |
| B37_End | Segment end position |
| cM | Segment size in centimorgans |
| grandparent | Assigned grandparent (added by the matching step) |
| source_sibling | Kit of the sibling whose triangulation file this came from |

### chromosome_matches.csv

Deduplicated version of matched_triangulations. One row per unique (Kit1_Number, Chr) combination.

| Column | Description |
|--------|-------------|
| name | Kit1 name |
| kit | Kit1 number |
| grandparent | Assigned grandparent |
| chr | Chromosome number |

### other_matches.csv

Cross-references chromosome matches against GEDmatch segment match data from `inputfiles/gedmatch/matches/`. Shows which siblings have a direct one-to-one segment match with the identified cousin.

| Column | Description |
|--------|-------------|
| chr | Chromosome number |
| cousin_kit | The identified cousin's kit number |
| cousin_name | The cousin's name |
| sibling_kit | Kit of the sibling who has a segment match |
| sibling_name | Name of the matching sibling |

## Per-Sibling Triangulation Dumps

### triangs-{sibling_kit}.csv

Raw triangulation data for a sibling across all chromosomes. One file per sibling. This is the unfiltered data as loaded from the input CSVs.

### triangs-{chr}-{sibling_kit}.csv

Triangulation data for a sibling filtered to a single chromosome. One file per (chromosome, sibling) combination.

## Per-Chromosome/Grandparent Breakdowns

### overlaps-{chr}-{grandparent}.csv

Calculated overlap regions for a specific chromosome and grandparent. These are the output of `OverlapCalculator` — regions where multiple siblings share DNA from the same grandparent.

| Column | Description |
|--------|-------------|
| Chr | Chromosome number |
| Grandparent | Grandparent name |
| B37_Start | Overlap start position |
| B37_End | Overlap end position |
| sibling_kits | List of sibling kits that overlap in this region |

### segments-{chr}-{grandparent}.csv

The grandparent segments (from `visualphasing.xlsx`) that were used as input to the overlap calculation for this chromosome/grandparent.

| Column | Description |
|--------|-------------|
| Chr | Chromosome number |
| Sibling | Sibling name |
| Kit | Sibling kit |
| Grandparent | Grandparent name |
| B37_Start | Segment start position |
| B37_End | Segment end position |

### all_overlaps.csv

All overlap records across all chromosomes and grandparents combined into a single file.
