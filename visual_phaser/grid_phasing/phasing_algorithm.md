# Grandparent Grid Phasing Algorithm

## Overview

Fill the Visual Phaser grid (2 rows per sibling per chromosome) in two phases:

**Phase 1 — Structural Phasing**: Fill cells with P1/P2 (paternal) and M1/M2 (maternal) using FIR/HIR/NIR pairwise data. M?/P? cousins classify RPs (which row changed). Every time a cell is set, immediately propagate left and right within that sibling's segment.

**Phase 2 — Labeling**: Map P1→PP/PM, P2→the other, M1→Ma/Mb, M2→the other using specific cousin matches (Amy=PM, etc.).

## Inputs

1. **Column boundaries** — base pair ranges from VP pixel widths
2. **RP assignments** — which sibling recombines at each column boundary (right edge)
3. **HIR/FIR tables** — pairwise segment data for all 10 sibling pairs
4. **Cousin definitions** — configurable list with grandparent affiliation

### Cousin Definitions

```python
COUSINS = [
    {"name": "Mickey", "grandparent": "M?"},
    {"name": "Amy",    "grandparent": "PM"},
]
```

Affiliations: `"PP"`, `"PM"`, `"P?"`, `"MP"`, `"MM"`, `"M?"`

### Cousin Recombination Filtering (before Phase 1)

A cousin's own recombination boundaries must be filtered out:
- If a cousin's match status changes at the same position for 3+ siblings AND that position is NOT a sibling RP → cousin recombination → merge segments across it
- Exception: don't merge for a sibling if the gap coincides with THAT sibling's own RP (it's a real sibling recombination there)

## Key Definitions

- **RP position**: Recombination at the **right edge** of the column. The RP column is the last column of the "before" state.
- **Segment**: Contiguous columns between a sibling's RPs. RP column is INCLUDED in its segment. Next segment starts at RP_column + 1.
- **Propagate left/right**: From a filled cell, carry values left and right to adjacent cells. At each of this sibling's RPs, use cousin data to determine which row flips (top or bottom), then continue with the flipped value. Stop at the chromosome edges.

## RP Classification (used during propagation)

At each sibling's RP, determine which row changed:
- Check M?/P? cousin match status at the RP column vs the next column
- **Maternal-side cousin** (M?, MP, MM): match changes → bottom changed, same → top changed
- **Paternal-side cousin** (P?, PP, PM): match changes → top changed, same → bottom changed
- Unknown → mark changing row as P? or M?

---

## PHASE 1: Structural Phasing

### Step 1: Build data structures

1. Extract column boundaries, RP assignments, HIR/FIR tables, cousin segments
2. Filter cousin recombinations
3. **Apply RP overrides**: Check the `RP_OVERRIDES` config for manually flagged bad RPs (identified by expert review of VP output). Remove any overridden RPs before phasing. Log each removal.
4. Compute each sibling's segments and RP count

### Step 2: Select anchor and initialize

1. Sort siblings by fewest RPs
2. Select the anchor (fewest RPs)
3. Pick a **middle column** of the anchor's longest segment
4. Set that cell: top = P1, bottom = M1
5. **Propagate left and right** from that cell within the anchor, using RP classification at each of the anchor's RPs to determine which row flips

After this step, the anchor has all columns filled with P1/P2 and M1/M2.

### Step 3: FIR Phase

Scan every filled column across all siblings. For each column that has a filled sibling:

1. Check all OTHER siblings at that column
2. For each unfilled sibling at that column, check if the pair is FIR (using the column midpoint against FIR segment data)
3. If **FIR** → copy BOTH values (top and bottom) from the filled sibling to the unfilled sibling at that column
4. **Immediately propagate** the newly set values left and right within that sibling's segments:
   - Walk left until hitting this sibling's RP or chromosome edge
   - Walk right until hitting this sibling's RP or chromosome edge
   - At each RP, classify which row changes (using cousin data) and flip accordingly
5. The propagation may fill many additional columns for this sibling
6. Each newly filled column creates new opportunities for FIR with other siblings

**Repeat** the entire FIR scan until no new cells are filled in a pass.

### Step 4: NIR Phase

Scan every unfilled cell. For each unfilled sibling at a column:

1. Check all other siblings at that column
2. If any other sibling has BOTH values set and the pair is **NIR** → set the unfilled sibling to the OPPOSITE of both values (P1↔P2, M1↔M2)
3. **Immediately propagate** left and right within that sibling's segments
4. Each newly filled cell creates new opportunities

**Repeat** until no new cells are filled.

Then **re-run FIR phase** (Step 3) since NIR may have created new FIR opportunities.

### Step 5: HIR Phase

Scan every unfilled cell. For each unfilled sibling at a column:

1. Check all other siblings at that column
2. If the unfilled sibling has ONE row filled (from a previous partial fill) and another sibling has BOTH values and the pair is **HIR**:
   - HIR means they share exactly one row
   - The filled row tells us which row matches → the other row must be different
   - Set the unfilled row accordingly
3. If the unfilled sibling has NO rows filled and another sibling has BOTH values and pair is **HIR**:
   - Use cousin data to determine which row is shared (same logic as before: maternal-side cousin same status → share maternal → flip paternal, etc.)
   - Set both values
4. **Immediately propagate** left and right
5. Each newly filled cell creates new opportunities

**Repeat** until no new cells are filled.

Then **re-run FIR and NIR phases** since HIR may have created new opportunities.

### Step 6: Structural Validation

After all phases complete:
1. Check FIR consistency: every FIR pair must have identical values at every column
2. Check NIR consistency: every NIR pair must have opposite values at every column
3. If contradictions found → the sibling with more contradictions may need a full flip (P1↔P2, M1↔M2)
4. After flipping, re-validate

### Step 7: Mark unknowns

Any cell still unfilled after all phases → mark as ("?", "?")

---

## PHASE 2: Labeling

### Step 8: Map P1/P2 → PP/PM

For each sibling:
1. Check if a specific paternal cousin (PP or PM) matches anywhere in a segment
2. If Amy (PM) matches a segment labeled P1 → P1=PM, P2=PP
3. If Amy matches a segment labeled P2 → P2=PM, P1=PP
4. Apply mapping to ALL columns for this sibling

If no direct cousin match for a sibling → propagate mapping via FIR with a sibling that has been resolved.

If still unresolved → keep as P1/P2 (or P?)

### Step 9: Map M1/M2 → Ma/Mb

Same logic with maternal cousins (MP, MM). If only M? cousins available → keep as M1/M2.

### Step 10: Write to Excel

Colors:
- PP → Magenta (FF00FF)
- PM → Lime (98FF00)
- Ma → Cyan (00FFFF)
- Mb → Gold (FFCC00)
- M1 → Cyan (00FFFF) — structural, unresolved
- M2 → Gold (FFCC00) — structural, unresolved
- P? / M? / ? → Grey (C0C0C0)

### Step 11: Retry with different anchor

Try up to 3 anchors (fewest RPs). Keep the result with most filled cells.

---

## Edge Cases

1. **RP at first/last column**: Same RP classification logic. If no "after" column → unknown.
2. **Consecutive sibling RPs**: Creates 1-column segments. Propagation stops immediately.
3. **No cousin data at RP**: Mark changing row as P? or M?.
4. **Multiple FIR references at same column**: All should agree (same values). If they conflict → flag.
5. **Wide columns straddling FIR/HIR boundaries**: Check at column midpoint. Since propagation is RP-driven (not per-column), this only matters for the initial FIR/NIR/HIR check.
6. **Adding new cousins**: Add DNA, run VP, add COUSINS entry. Phase 1 unchanged; Phase 2 gains more labeling power.

## Validation Checks

After Phase 1:
1. Each sibling's values only change at their own RP columns
2. FIR pairs have identical P1/P2 and M1/M2 at every column
3. NIR pairs have opposite P1/P2 and M1/M2 at every column

After Phase 2:
4. Cousin labels consistent with mapped PP/PM/Ma/Mb
5. FIR pairs still have identical final labels

## Trace Log

When `--log` flag is used, generate `logs/chr{N}_decisions.md` with:
- Data summary (columns, RPs, cousin segments)
- Anchor selection reasoning
- Cousin recombination filtering decisions
- Every cell set: which sibling, which column, what values, why (FIR/NIR/HIR with whom)
- Every propagation: direction, RPs crossed, values flipped
- Phase 2 label mapping per sibling
- Validation results
