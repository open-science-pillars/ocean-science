---
type: dataset
title: ECCO v4 Release 4 ocean state estimate
description: "Dynamically consistent global ocean state estimate, 1992-2017, llc90 native grid; budgets close exactly; no formal error fields."
tags: [ecco, state-estimate, llc90, podaac, ocean]
generated: { by: knowledge-seeder/claude, at: 2026-07-06T00:00:00Z }
resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_TEMP_SALINITY_LLC0090GRID_MONTHLY_V4R4
version: "V4r4, 1992-2017 (ShortNames CMR-verified and native granules live-loaded 2026-07-04)"
status: stable
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
trainings:
  - https://ecco-v4-python-tutorial.readthedocs.io/
stale_after: 2027-01-04
---

# ECCO v4 Release 4 ocean state estimate

**Identity.** The Estimating the Circulation and Climate of the Ocean
version 4 release 4 state estimate: the MITgcm on the llc90 grid
(nominal 1 degree, 50 levels, 13 tiles), fit to two and a half decades
of observations by adjusting controls (initial conditions, atmospheric
forcing, mixing parameters), never by inserting data increments. Period
1992 through 2017, monthly and daily means plus daily snapshots.
Product family and archive: PO.DAAC, ShortNames per the fields
concepts ([fields index](../fields/ecco-v4r4/index.md), one concept per
collection family, each carrying the CMR sweep that confirmed its
ShortNames; 51 llc90 collections first verified against CMR
2026-07-04); project page https://ecco-group.org/products-ECCO-V4r4.htm.

**Structure.** Native output dims `(time, tile, k, j, i)` with 2D
curvilinear coordinates; C-grid staggering; partial cells (hFac).
Tracer flavors: `THETA` is potential temperature, `SALT` is practical
salinity (PSS-78). Flux variables with a MASS suffix (or documented as
cell-integrated) already carry hFac; applying the partial-cell factor a
second time double-counts it, a standard budget bug
([ecco-velmass-hfac-double-count](../gotchas/ecco-velmass-hfac-double-count.md)).
Convenience 0.5 degree interpolated collections exist (`05DEG` in the
ShortName) for display and comparison; conservation properties live
only on the native grid (see
[ecco-native-vs-regridded](../gotchas/ecco-native-vs-regridded.md)).

**Access.** Time-ranged collections load with ecco_access using EXACT
ShortNames (bare variable-name queries open an interactive picker,
which hangs scripted use; observed 2026-07-04); static collections
(geometry, mixing coefficients) load through earthaccess instead
([ecco-access-static-collections](../gotchas/ecco-access-static-collections.md)).
Earthdata Login required. A 2010 native THETA year is about 209 MB and
loaded in seconds in verification.

## Citation

PO.DAAC prescribes one citation form for every V4r4 collection (the
Citation block on each dataset landing page, for example the
[temperature and salinity landing page](https://podaac.jpl.nasa.gov/dataset/ECCO_L4_TEMP_SALINITY_LLC0090GRID_MONTHLY_V4R4)),
with the collection title, its DOI, and the access date filled per
collection:

> ECCO Consortium, Fukumori, I., Wang, O., Fenty, I., Forget, G.,
> Heimbach, P., & Ponte, R. M.. 2021. [Collection title] (Version 4
> Release 4). Ver. V4r4. PO.DAAC, CA, USA. Dataset accessed
> [YYYY-MM-DD] at https://doi.org/10.5067/[collection DOI suffix]

The creator list, the 2021 year, and the PO.DAAC publisher are the
same for all 90 collections; CMR carries the creator list and the
publisher in each collection's citation record, with a release date of
2021-04-19. Cite every collection an analysis touched, not the product
as a whole. The per-collection DOIs live with the fields
concepts and in `tools/ecco_v4r4_dois.yaml`, and `tools/ecco_cite.py
cite` renders this form for a list of ShortNames (its selftest checks
the creator list, year, and publisher above against its template).

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
  corrections with signal (Variants sections of the
  [SSH](../fields/ecco-v4r4/ssh.md) and [OBP](../fields/ecco-v4r4/obp.md)
  fields concepts).
- [ecco-mht-basin-scope](../gotchas/ecco-mht-basin-scope.md): a
  meridional heat transport with no basin mask is the full latitude
  circle, not the Atlantic section RAPID observes.
- [ecco-trend-without-effective-n](../gotchas/ecco-trend-without-effective-n.md):
  monthly series are serially correlated; a trend without an
  effective-sample-size interval overstates certainty, and the
  bundle's own twelve-month steric trend is the example.
- [ecco-velmass-hfac-double-count](../gotchas/ecco-velmass-hfac-double-count.md):
  the MASS-suffixed velocities already carry hFac; a transport that
  applies it again is biased low.
- [ecco-access-static-collections](../gotchas/ecco-access-static-collections.md):
  ecco_access 0.3.1 guesses a dated filename for the static
  collections; fetch geometry and mixing coefficients through CMR with
  earthaccess.
