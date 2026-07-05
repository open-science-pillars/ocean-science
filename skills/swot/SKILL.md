---
name: swot
description: SWOT KaRIn L2 SSH: product tiers, orbit phases (1-day cal/val vs 21-day science), two-swath geometry, cycle/pass naming, earthaccess.
user-invocable: false
---

# swot

Background expertise for SWOT KaRIn sea surface height work. Authored
in Session 8b per SPECIFICATION.md v0.5.1 §4.3. Product inventory,
granule anatomy, and orbit-phase details live in
`references/swot-products.md` (CMR-verified 2026-07-04); the current
processing baseline and the uncertainty variables live in
`knowledge/datasets/swot-karin.md` with a verification date, never
hardcoded.

## Knowledge first

Before any SWOT analysis, consult and restate what applies:

1. `knowledge/datasets/swot-karin.md`: version families, current
   baseline state, the Uncertainty section (which ssha uncertainty
   variables exist and what they do not cover), and the Known issues
   list (crossover calibration arrives unapplied in ssha_karin;
   CRIDs drift within collections).
2. `knowledge/gotchas/swot-calval-orbit-phases.md`: any date range
   touching 2023 gets the orbit-phase check FIRST; ranges spanning the
   July 2023 transition mix incompatible sampling regimes, and
   cal/val-era queries on Version C collections return empty silently.

## What KaRIn SSH is, in one paragraph

Wide-swath interferometric altimetry: two 50 km swaths of 2 km-posted
sea surface height (250 m unsmoothed tier) separated by a ~20 km nadir
gap, resolving two-dimensional SSH structure at scales conventional
altimetry cannot. The price: swath geometry (cross-track systematic
errors, signed cross-track coordinates, the gap), phase-dependent
sampling, and bit-packed quality flags that gate every pixel.

## Choosing a tier

Basic for SSH anomaly work; Expert when corrections or the full
uncertainty variable set are needed; WindWave for wind and wave state;
Unsmoothed only when 250 m structure is the point (large granules).
Tier choice is per the reference's table; version family (C vs D) is
per the dataset concept's current-baseline note.

## Working rules

- **Flags gate pixels:** decode the bit-packed quality flags before
  statistics (quality-control's decoding rules apply); report the
  fraction masked and why. Flag gating alone does not make ssha
  statistics safe: crossover calibration (height_cor_xover) arrives
  unapplied, per the dataset concept's known issue.
- **Respect the swath structure:** summaries and grids are per-swath
  with the nadir gap intact; never interpolate across the gap; treat
  left and right swaths as having distinct error profiles.
- **Cycle/pass is the unit of acquisition:** regional work means
  spatial search over passes, then trimming; a "cycle" means a
  different duration in each orbit phase.
- **ssha uncertainty variables travel with the data:** quote them with
  results per the house uncertainty rule, with the caveats the dataset
  concept records.
- Loading is the load-swot workflow's job (volume gate, flag decode,
  swath-aware summary); this skill supplies what it restates.

## Hydrology

SWOT river, lake, and inundation products exist as separate
collections and are DEFERRED to the hydrology plugin (Phase 2); this
plugin's SWOT scope is KaRIn L2 SSH and the nadir altimeter products.

## Must NOT

- Never analyze across the cal/val-to-science transition as one
  homogeneous record.
- Never treat an empty result for early-mission dates as "no data"
  before checking the version family.
- Never use unflagged pixels in statistics.
- Never interpolate across the nadir gap.
- Never hardcode a processing baseline; read the dataset concept and
  record what the granules actually carry.
- Never quote swath or regional ssha statistics without stating
  whether height_cor_xover was applied.
