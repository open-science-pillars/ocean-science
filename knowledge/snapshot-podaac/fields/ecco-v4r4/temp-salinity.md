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
  - id: family-manifest
    resource: ../../../../tools/ecco_v4r4_families.yaml
    title: ECCO V4r4 family manifest, the per-variable record of the granule verifications of 2026-07-04 and 2026-08-30 (held to each Schema by tools/check_fields.py)
  - id: fixtures-2010
    resource: ../../references/retrieval/fixtures-2010-manifest.json
    title: The manifested 2010 native fixtures (SHA-512 per granule) the dims were re-verified against
verified:
  - { by: process:cmr-shortname-sweep, at: 2026-08-30T20:07:19Z }
  - { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
---

# Ocean potential temperature and salinity

The tracer state of the ECCO V4r4 estimate, 1992 through 2017: potential
temperature and practical salinity on the native llc90 grid (13 tiles, 50
levels) and the interpolated 0.5 degree grid.[^podaac-landing] The
monthly llc90 collection was granule-verified live on 2026-07-04 and
re-verified 2026-09-04 against the manifested 2010 fixtures: 12 monthly
granules, each time/k/tile/j/i = 1/50/13/90/90, so 12/50/13/90/90
concatenated.[^family-manifest][^fixtures-2010] The
snapshot collection carries the month-boundary states that budget
tendency terms are formed from.

# Schema

| Variable | Units | Grid point | Description | Provenance |
|---|---|---|---|---|
| `THETA` | degree_C | c center | Potential temperature | granule-verified 2026-07-04 |
| `SALT` | 1e-3 | c center | Practical salinity (PSS-78) | granule-verified 2026-08-30 |

# Variants

All five ShortNames verified in CMR by the 2026-08-30 sweep.[^cmr-sweep]

- `ECCO_L4_TEMP_SALINITY_LLC0090GRID_MONTHLY_V4R4`: native llc90, monthly mean. DOI: 10.5067/ECL5M-OTS44.
- `ECCO_L4_TEMP_SALINITY_LLC0090GRID_DAILY_V4R4`: native llc90, daily mean. DOI: 10.5067/ECL5D-OTS44.
- `ECCO_L4_TEMP_SALINITY_LLC0090GRID_SNAPSHOT_V4R4`: native llc90, instantaneous snapshots (budget bookends). DOI: 10.5067/ECL5S-OTS44.
- `ECCO_L4_TEMP_SALINITY_05DEG_MONTHLY_V4R4`: 0.5 degree interpolated, monthly mean; display and comparison, not budgets. DOI: 10.5067/ECG5M-OTS44.
- `ECCO_L4_TEMP_SALINITY_05DEG_DAILY_V4R4`: 0.5 degree interpolated, daily mean; display and comparison, not budgets. DOI: 10.5067/ECG5D-OTS44.

# Known issues

Conservation properties live only on the native grid; interpolated
collections do not close budgets
([ecco-native-vs-regridded](../../gotchas/ecco-native-vs-regridded.md)).

[^podaac-landing]: PO.DAAC dataset landing page
[^cmr-sweep]: CMR ShortName sweep, tools/verify_cmr.py
[^family-manifest]: ECCO V4r4 family manifest, tools/ecco_v4r4_families.yaml
[^fixtures-2010]: references/retrieval/fixtures-2010-manifest.json, the manifested 2010 native fixtures
