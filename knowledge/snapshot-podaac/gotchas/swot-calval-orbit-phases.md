---
type: dataset-gotcha
title: "SWOT orbit phases: cal/val and science data are not one record"
description: "Date ranges spanning July 2023 mix a 1-day repeat and a 21-day orbit with different cycle numbering; cal/val data exists only in the D version family."
tags: [swot, orbit, calval, cycles]
generated: { by: knowledge-seeder/claude, at: 2026-07-04T00:00:00Z }
severity: high
dataset: ../datasets/swot-karin.md
eval_case: swot-calval-window
sources:
  - id: nasa-swot-l2-lr-ssh-d
    resource: https://podaac.jpl.nasa.gov/dataset/SWOT_L2_LR_SSH_D
    title: "PO.DAAC collection page: SWOT_L2_LR_SSH_D (Version D umbrella)"
  - id: nasa-swot-l2-lr-ssh-2
    resource: https://podaac.jpl.nasa.gov/dataset/SWOT_L2_LR_SSH_2.0
    title: "PO.DAAC collection page: SWOT_L2_LR_SSH_2.0 (Version C umbrella)"
  - id: version-d-release-note
    resource: https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/web-misc/swot_mission_docs/SWOT_VersionD_KaRIn_Products_Release_Note_20250423b.pdf
    title: "Release Note: SWOT Version D KaRIn Science Data Products, JPL, 2025-04-23: Table 2 orbit and mission phase timeline, CRID scope by phase and repeat cycle"
  - id: swot-karin
    resource: ../datasets/swot-karin.md
    title: "SWOT KaRIn Level 2 Low Rate SSH, the dataset concept: Variants and the family holdings probe"
status: stable
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
stale_after: 2027-01-04
---

# SWOT orbit phases: cal/val and science data are not one record

**Mechanism.** SWOT flew a 1-day repeat cal/val orbit from early 2023
until July 2023 (1-day repeat from 2023-01-14, calibration phase
2023-03-30 to 2023-07-10), then moved to the 21-day science orbit
(from 2023-07-21).[^version-d-release-note] The phases differ in
everything an analysis touches: spatial coverage (a sparse fixed track
set vs global), temporal sampling (daily revisits vs 21-day), and
cycle numbering (cal/val cycles in the 400-500s, 475 to 578; science
cycles restart at 001).[^version-d-release-note] Additionally, the
version families split the record: as probed 2026-07-04, cal/val-era
granules exist only in the `*_D` collections (cycle 477 granules
returned for 2023-04), while `*_2.0` (Version C) collections return
ZERO granules for the same
window.[^nasa-swot-l2-lr-ssh-d][^nasa-swot-l2-lr-ssh-2]

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

**Verification.** Reproduced 2026-07-04 and again 2026-09-04 by
public CMR granule search: BASIC_2.0 returned 0 granules for
2023-04-01..02 while BASIC_D returned cycle-477 granules
(`SWOT_L2_LR_SSH_Basic_477_022_20230401T..._PGD0_01.nc`); science-era
BASIC_2.0 granules carry cycles 001+ (011 in 2024-03). The dataset
concept records the whole-family holdings behind this: every Version C
tier begins at cycle 001 (2023-07-26) and holds nothing in the
calibration window, every Version D tier begins at cycle 473
(2023-03-27).[^swot-karin] The release note describes the Version C
PGC0 reprocessing as spanning calibration cycles 475 to 578, yet the
`*_2.0` collections in CMR hold none of it; the archive's holdings,
not the release note, decide what a query returns.[^version-d-release-note]

[^nasa-swot-l2-lr-ssh-d]: PO.DAAC collection page: SWOT_L2_LR_SSH_D (Version D umbrella)
[^nasa-swot-l2-lr-ssh-2]: PO.DAAC collection page: SWOT_L2_LR_SSH_2.0 (Version C umbrella)
[^version-d-release-note]: Release Note: SWOT Version D KaRIn Science Data Products, JPL, 2025-04-23, Table 2 (1-day repeat orbit from 2023-01-14, calibration phase 2023-03-30 to 2023-07-10, 21-day repeat orbit and science phase from 2023-07-21) and section 3 (PGD0 spans calibration cycles 475 to 578 and science cycles 1 to 31; PGC0 the same calibration cycles and science cycles 1 to 9); fetched and read 2026-09-04
[^swot-karin]: SWOT KaRIn Level 2 Low Rate SSH, the dataset concept, Variants: family holdings from the public CMR granule probe of 2026-09-04
