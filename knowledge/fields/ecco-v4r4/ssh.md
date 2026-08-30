---
type: Data Collection
title: Sea surface height
description: "The SSH family of the V4r4 estimate: dynamic sea surface height and model sea level anomaly, with snapshot bookends for budgets and a corrected V4R4B re-release for this family."
tags: [ecco, v4r4, sea-surface-topography, geodesy]
resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4
status: stable
generated: { by: claude-code/fable-5, at: 2026-08-30T20:05:00Z }
stale_after: 2027-01-04
sources:
  - id: podaac-landing
    resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4
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

# Sea surface height

Dynamic sea surface height and model sea level anomaly from the ECCO
V4r4 ocean and sea-ice state estimate, on the native llc90 grid and the
interpolated 0.5 degree grid, monthly and daily means plus
instantaneous snapshots.[^podaac-landing] The snapshot collection's
`ETAN` provides the month-boundary states that form the z* scale factor
in property budgets.[^variable-catalog] Sea surface height and ocean
bottom pressure are the two V4r4 families that ship a corrected V4R4B
re-release alongside the original V4R4 collections; an analysis that
mixes the two releases folds the baseline correction into the signal
(the release-mixing gotcha below records the mechanism).[^variable-catalog]

# Schema

| Variable | Units | Grid point | Description | Provenance |
|---|---|---|---|---|
| `SSH` | m | c center | Dynamic sea surface height | granule-verified 2026-08-30 |
| `SSHIBC` | m | c center | Inverse-barometer contribution to sea surface height, per the user guide convention | granule-verified 2026-08-30 |
| `SSHNOIBC` | m | c center | Sea surface height without the inverse-barometer correction | granule-verified 2026-08-30 |
| `ETAN` | m | c center | Model sea level anomaly; feeds the z* scale factor in budgets | granule-verified 2026-08-30 |

# Variants

All nine ShortNames verified in CMR by the 2026-08-30 sweep.[^cmr-sweep]
V4R4B lines carry the corrected geodetic re-release for this family; a
series or comparison spanning V4R4 and V4R4B conflates the correction
with signal.

- `ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4`: native llc90, monthly mean.
- `ECCO_L4_SSH_LLC0090GRID_DAILY_V4R4`: native llc90, daily mean.
- `ECCO_L4_SSH_LLC0090GRID_SNAPSHOT_V4R4`: native llc90, instantaneous snapshots (budget bookends; ETAN for z*).
- `ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4B`: native llc90, monthly mean, corrected V4R4B release.
- `ECCO_L4_SSH_LLC0090GRID_DAILY_V4R4B`: native llc90, daily mean, corrected V4R4B release.
- `ECCO_L4_SSH_05DEG_MONTHLY_V4R4`: 0.5 degree interpolated, monthly mean; display and comparison, not budgets.
- `ECCO_L4_SSH_05DEG_DAILY_V4R4`: 0.5 degree interpolated, daily mean; display and comparison, not budgets.
- `ECCO_L4_SSH_05DEG_MONTHLY_V4R4B`: 0.5 degree interpolated, monthly mean, corrected V4R4B release.
- `ECCO_L4_SSH_05DEG_DAILY_V4R4B`: 0.5 degree interpolated, daily mean, corrected V4R4B release.

# Known issues

Mixing V4R4 and V4R4B collections in one analysis conflates the
baseline correction with the geophysical signal
([ecco-release-mixing](../../gotchas/ecco-release-mixing.md)).

[^podaac-landing]: PO.DAAC dataset landing page
[^cmr-sweep]: CMR ShortName sweep, tools/verify_cmr.py
[^variable-catalog]: OSP ECCO variable catalog (sweep of 2026-07-04)
