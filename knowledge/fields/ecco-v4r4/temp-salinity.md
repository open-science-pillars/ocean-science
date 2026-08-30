---
type: Data Collection
title: Ocean potential temperature and salinity
description: "The THETA and SALT family: the tracer state of the V4r4 estimate on native and interpolated grids, with the snapshot collections that bookend budgets."
tags: [ecco, v4r4, ocean-temperature, salinity-density]
resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_TEMP_SALINITY_LLC0090GRID_MONTHLY_V4R4
status: stable
generated: { by: ecco-scout/claude, at: 2026-08-28T00:00:00Z }
stale_after: 2027-01-04
sources:
  - id: podaac-landing
    resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_TEMP_SALINITY_LLC0090GRID_MONTHLY_V4R4
    title: PO.DAAC dataset landing page
  - id: cmr-sweep
    resource: all ECCO_L4_*V4R4* collections in CMR (provider POCLOUD)
    title: CMR ShortName sweep, tools/verify_cmr.py
  - id: variable-catalog
    resource: https://github.com/open-science-pillars/ocean-science/blob/main/skills/ecco/references/variable-catalog.md
    title: OSP ECCO variable catalog (sweep of 2026-07-04)
    author: human:PaulMRamirez
verified:
  - { by: process:cmr-shortname-sweep, at: 2026-08-30T20:07:19Z }
  - { by: human:PaulMRamirez, at: 2026-08-30T20:30:00Z }
---

# Ocean potential temperature and salinity

The tracer state of the ECCO V4r4 estimate, 1992 through 2017: potential
temperature and practical salinity on the native llc90 grid (13 tiles, 50
levels) and the interpolated 0.5 degree grid.[^podaac-landing] The
monthly llc90 collection was granule-verified live on 2026-07-04 (12
granules, dims time/k/tile/j/i = 12/50/13/90/90).[^variable-catalog] The
snapshot collection carries the month-boundary states that budget
tendency terms are formed from.

# Schema

| Variable | Units | Grid point | Description | Provenance |
|---|---|---|---|---|
| `THETA` | degree_C | c center | Potential temperature | granule-verified 2026-07-04 |
| `SALT` | 1e-3 | c center | Practical salinity (PSS-78) | granule-verified 2026-08-30 |

# Variants

- `ECCO_L4_TEMP_SALINITY_LLC0090GRID_MONTHLY_V4R4`: native llc90, monthly mean.
- `ECCO_L4_TEMP_SALINITY_LLC0090GRID_DAILY_V4R4`: native llc90, daily mean.
- `ECCO_L4_TEMP_SALINITY_LLC0090GRID_SNAPSHOT_V4R4`: native llc90, instantaneous snapshots (budget bookends).
- `ECCO_L4_TEMP_SALINITY_05DEG_MONTHLY_V4R4`: 0.5 degree interpolated, monthly mean; display and comparison, not budgets.
- `ECCO_L4_TEMP_SALINITY_05DEG_DAILY_V4R4`: 0.5 degree interpolated, daily mean; display and comparison, not budgets.

# Known issues

Conservation properties live only on the native grid; interpolated
collections do not close budgets
([ecco-native-vs-regridded](../../gotchas/ecco-native-vs-regridded.md)).

[^podaac-landing]: PO.DAAC dataset landing page
[^variable-catalog]: OSP ECCO variable catalog (sweep of 2026-07-04)
