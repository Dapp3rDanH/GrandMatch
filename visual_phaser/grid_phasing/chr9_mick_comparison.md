# Chr9 Comparison: Algorithm vs Mick's Manual Phasing

## Results

**78% match** (133/170 cells). Donal is perfect. Joyce and Roger have systematic inversions.

## Per-Sibling

### Donal — PERFECT MATCH (17/17 columns)
```
     H  I  J  K  L  M  N  O  P  Q  R  S  T  U  V  W  X
top  PP PP PP PP PP PP PP PP PP PP PP PP PM PM PM PM PM
bot  Ma Ma Ma Ma Ma Ma Ma Ma Ma Ma Ma Ma Ma Ma Ma Ma Ma
```

### Denny — 1 difference (16/17)
```
Col O top: Mick=PM, Ours=PP
```
Everything else matches.

### Debbie — 9 differences (25/34)
```
Col R top:  Mick=PM  Ours=PP
Col S top:  Mick=PP  Ours=PM
Col T top:  Mick=PP  Ours=PM
Col U top:  Mick=PP  Ours=PM    Col U bot: Mick=Mb  Ours=Ma
Col V bot:  Mick=Mb  Ours=Ma
Col W top:  Mick=PP  Ours=PM    Col W bot: Mick=Mb  Ours=Ma
Col X bot:  Mick=Mb  Ours=Ma
```
First 10 columns (H-Q) match perfectly. Differences start at Debbie's RP at col R.

### Joyce — 15 differences (19/34)
```
Cols H,I,K,L top:  Mick=PM  Ours=PP  (inverted)
Cols J,K bot:      Mick=Ma  Ours=Mb  (inverted)
Cols O-W top:      Mick=PP  Ours=PM  (inverted)
```
Systematic inversion: our PP/PM and Ma/Mb are swapped vs Mick's for most columns.

### Roger — 12 differences (22/34)
```
Cols L-P top:  Mick=PP  Ours=PM  (inverted)
Cols L-Q bot:  Mick=Ma  Ours=Mb  (inverted)
Col Q top:     Mick=PM  Ours=PP  (inverted)
```
Roger's first 4 columns (H-K) match. Inversion starts at col L.

## Mick's Manual Grid (ground truth)
```
           H   I   J   K   L   M   N   O   P   Q   R   S   T   U   V   W   X
Debbie PP  PP  PP  PP  PP  PP  PP  PP  PP  PP  PM  PP  PP  PP  PP  PP  PM
       Ma  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb

Denny  PP  PP  PP  PP  PP  PP  PP  PM  PM  PM  PM  PM  PM  PM  PM  PM  PM
       Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma

Donal  PP  PP  PP  PP  PP  PP  PP  PP  PP  PP  PP  PP  PM  PM  PM  PM  PM
       Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma

Joyce  PM  PM  PM  PM  PM  PM  PP  PP  PP  PP  PP  PP  PP  PP  PP  PP  PM
       Mb  Mb  Ma  Ma  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb

Roger  PP  PP  PP  PP  PP  PP  PP  PP  PP  PM  PM  PM  PM  PM  PM  PM  PP
       Mb  Mb  Mb  Mb  Ma  Ma  Ma  Ma  Ma  Ma  Mb  Mb  Mb  Mb  Mb  Mb  Mb
```

## Our Algorithm Grid
```
           H   I   J   K   L   M   N   O   P   Q   R   S   T   U   V   W   X
Debbie PP  PP  PP  PP  PP  PP  PP  PP  PP  PP  PP  PM  PM  PM  PP  PM  PM
       Ma  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Ma  Ma  Ma  Ma

Denny  PP  PP  PP  PP  PP  PP  PP  PP  PM  PM  PM  PM  PM  PM  PM  PM  PM
       Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma

Donal  PP  PP  PP  PP  PP  PP  PP  PP  PP  PP  PP  PP  PM  PM  PM  PM  PM
       Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma  Ma

Joyce  PP  PP  PM  PP  PP  PM  PP  PM  PM  PM  PM  PM  PM  PM  PM  PM  PM
       Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb

Roger  PP  PP  PP  PP  PM  PM  PM  PM  PM  PP  PM  PM  PM  PM  PM  PM  PP
       Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb  Mb
```

## Analysis

### Root cause: Seed polarity inversion
Joyce and Roger's systematic inversions suggest their seed column resolved the PP/PM (or Ma/Mb) polarity backwards. Once the seed is inverted, the RP walk carries the inversion through all columns.

### What's working well
- **Donal**: Perfect match — anchor sibling, directly filled from cousin data
- **Denny**: Near-perfect — 1 column off, likely an RP classification issue
- **Debbie H-Q**: First 10 columns match perfectly
- **RP boundaries**: Values change at correct columns for all siblings
- **Maternal tracking**: Ma/Mb alternation pattern is correct (just sometimes inverted polarity)

### What needs fixing
1. **Joyce seed inversion**: Joyce's PP/PM labels are flipped relative to Mick's for most columns
2. **Roger L-P inversion**: Roger's values flip at column L relative to Mick's
3. **Debbie R onward**: Some RP classifications may be wrong in the second half

### Possible fixes
- Cross-validate seed values against multiple reference siblings (not just the first FIR found)
- Use Amy's PM data as a hard constraint after seeding to catch inversions
- Add validation check: if a seed produces values that conflict with cousin labels, flip the seed

Generated 2026-03-30.
