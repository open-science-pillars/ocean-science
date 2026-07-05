---
type: dataset
title: GRACE/GRACE-FO JPL mascon solutions
description: "Monthly mass anomaly (equivalent water thickness) on 3-degree mascons, RL06.3 version 4; formal per-mascon uncertainty grids ship with the data."
tags: [grace, grace-fo, mascons, mass, podaac]
timestamp: 2026-07-04
resource: https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4
version: "JPL RL06.3 version 4, CMR-verified 2026-07-04; CRI-filtered grid (TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4) and unfiltered grid (TELLUS_GRAC-GRFO_MASCON_GRID_RL06.3_V4) both live"
status: verified
verified: 2026-07-04
verified_by: Paul Ramirez (steward pro tem)
---

# GRACE/GRACE-FO JPL mascon solutions

**Identity.** Monthly surface mass anomalies (expressed as equivalent
water thickness) estimated directly on 3-degree spherical-cap mass
concentration blocks (mascons) from GRACE (2002-2017) and GRACE-FO
(2018-present) inter-satellite ranging; the JPL solution line, RL06.3
v4 as of the verification date. Distributed as 0.5-degree grids that
REPRESENT the 3-degree mascons: the native information scale is the
mascon, not the grid cell. The CRI-filtered variant separates
coastline-straddling mascons into land and ocean parts; derived
Tellus time series (ocean mass, Greenland, Antarctica) are separate
collections.

**Structure.** Monthly fields of water-equivalent thickness anomaly
against a stated baseline period, with scale/gain guidance and the
uncertainty grids below; a GIA correction (a specific model, per the
product documentation) is already applied to the standard product.
Month gaps exist (battery management eras, the 2017-2018
GRACE-to-GRACE-FO gap).

## Uncertainty

- **Formal per-mascon uncertainty grids ship with the product**:
  monthly 1-sigma estimates per mascon. They capture solution noise,
  scale with latitude and month, and are the quantitative floor for
  any mass statement.
- The formal errors do NOT include the two dominant systematic terms:
  coastal leakage (its own gotcha) and the GIA model choice (its own
  gotcha); both exceed the formal errors regionally.
- Averaging mascons reduces noise slower than white-noise intuition
  suggests (mascon errors are spatially correlated); basin averages
  quote the product's guidance, not sqrt(N).

## Known issues

- [grace-coastal-leakage](../gotchas/grace-coastal-leakage.md)
- [grace-gia-correction](../gotchas/grace-gia-correction.md)
- The 2017-2018 inter-mission gap breaks trend fits that treat the
  record as continuous; fit with the gap acknowledged.
