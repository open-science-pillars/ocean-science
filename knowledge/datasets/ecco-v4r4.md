---
type: dataset
title: ECCO v4 Release 4 ocean state estimate
description: "Dynamically consistent global ocean state estimate, 1992-2017, llc90 native grid; budgets close exactly; no formal error fields."
tags: [ecco, state-estimate, llc90, podaac, ocean]
timestamp: 2026-07-04
resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_TEMP_SALINITY_LLC0090GRID_MONTHLY_V4R4
version: "V4r4, 1992-2017 (ShortNames CMR-verified and native granules live-loaded 2026-07-04)"
status: verified
verified: 2026-07-04
verified_by: OSP steward review
trainings:
  - https://ecco-v4-python-tutorial.readthedocs.io/
---

# ECCO v4 Release 4 ocean state estimate

**Identity.** The Estimating the Circulation and Climate of the Ocean
version 4 release 4 state estimate: the MITgcm on the llc90 grid
(nominal 1 degree, 50 levels, 13 tiles), fit to two and a half decades
of observations by adjusting controls (initial conditions, atmospheric
forcing, mixing parameters), never by inserting data increments. Period
1992 through 2017, monthly and daily means plus daily snapshots.
Product family and archive: PO.DAAC, ShortNames per this plugin's
variable catalog (51 llc90 collections verified against CMR
2026-07-04); project page https://ecco-group.org/products-ECCO-V4r4.htm.

**Structure.** Native output dims `(time, tile, k, j, i)` with 2D
curvilinear coordinates; C-grid staggering; partial cells (hFac).
Convenience 0.5 degree interpolated collections exist (`05DEG` in the
ShortName) for display and comparison; conservation properties live
only on the native grid (see
[ecco-native-vs-regridded](../gotchas/ecco-native-vs-regridded.md)).

**Access.** Time-ranged collections load with ecco_access using EXACT
ShortNames (bare variable-name queries open an interactive picker,
which hangs scripted use; observed 2026-07-04); static collections
(geometry, mixing coefficients) via earthaccess, since ecco_access
synthesizes nonexistent dated filenames for them (observed 2026-07-04).
Earthdata Login required. A 2010 native THETA year is about 209 MB and
loaded in seconds in verification.

## Uncertainty

**ECCO v4r4 ships no formal error or uncertainty fields.** No per-value
standard error exists anywhere in the product. What stands in for
formal errors:

- **Dynamical consistency**: model physics hold exactly, so property
  budgets close to machine precision and transports are
  self-consistent; this constrains internal consistency, not accuracy
  against the real ocean.
- **Comparison spread against independent observations** (for example
  the RAPID array for Atlantic transport) provides empirical
  uncertainty for specific quantities; validated recipes record these
  as expected-uncertainty ranges.
- The estimate is smooth by construction (no eddies at 1 degree);
  eddy-scale variance is absent, not uncertain.

The uncertainty statements available for any derived quantity are a
recipe's expected-uncertainty range or the plain fact that ECCO
provides no formal uncertainty for it.

## Known issues

- [ecco-native-vs-regridded](../gotchas/ecco-native-vs-regridded.md)
- [ecco-geothermal-flux](../gotchas/ecco-geothermal-flux.md)
- [ecco-release-mixing](../gotchas/ecco-release-mixing.md): SSH and OBP
  have corrected `V4R4B` collections; mixing releases conflates baseline
  corrections with signal (variable catalog, Variants section).
- [ecco-mht-basin-scope](../gotchas/ecco-mht-basin-scope.md): a
  meridional heat transport with no basin mask is the full latitude
  circle, not the Atlantic section RAPID observes.
