---
type: dataset-gotcha
title: "SWOT orbit phases: cal/val and science data are not one record"
description: "Date ranges spanning July 2023 mix a 1-day repeat and a 21-day orbit with different cycle numbering; cal/val data exists only in the D version family."
tags: [swot, orbit, calval, cycles]
timestamp: 2026-07-04
severity: high
dataset: ../datasets/swot-karin.md
eval_case: swot-calval-window
evidence:
  - https://podaac.jpl.nasa.gov/dataset/SWOT_L2_LR_SSH_D
  - https://podaac.jpl.nasa.gov/dataset/SWOT_L2_LR_SSH_2.0
  - https://github.com/open-science-pillars/ocean-science/blob/main/skills/swot/references/swot-products.md
status: verified
verified: 2026-07-04
verified_by: OSP steward review
---

# SWOT orbit phases: cal/val and science data are not one record

**Mechanism.** SWOT flew a 1-day repeat cal/val orbit from early 2023
until July 2023, then moved to the 21-day science orbit. The phases
differ in everything an analysis touches: spatial coverage (a sparse
fixed track set vs global), temporal sampling (daily revisits vs
21-day), and cycle numbering (cal/val cycles in the 400-500s; science
cycles restart at 001). Additionally, the version families split the
record: as probed 2026-07-04, cal/val-era granules exist only in the
`*_D` collections (cycle 477 granules returned for 2023-04), while
`*_2.0` (Version C) collections return ZERO granules for the same
window.

**Wrong-result mode.** Two silent failures: (1) a time series or
statistics window spanning July 2023 mixes incompatible sampling
regimes, aliasing the orbit change into apparent variability; (2) a
cal/val-era query against a Version C collection returns empty and
reads as "no data for those dates", when the data exists in the D
family.

**Correct approach.** Any request touching 2023 gets the phase check
first: ranges spanning the transition are split at it (or narrowed to
one phase) and analyzed per phase; cal/val-era work uses the D-family
collections; cycle numbers are interpreted per phase. The load-swot
workflow surfaces this concept whenever the range applies.

**Verification.** Reproduced 2026-07-04: BASIC_2.0 returned 0 granules
for 2023-04-01..02 while BASIC_D returned cycle-477 granules
(`SWOT_L2_LR_SSH_Basic_477_022_20230401T..._PGD0_01.nc`); science-era
BASIC_2.0 granules carry cycles 001+ (011 in 2024-03).
