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
  - id: family-manifest
    resource: ../../../../tools/ecco_v4r4_families.yaml
    title: ECCO V4r4 family manifest, the per-variable record of the granule verifications of 2026-07-04 and 2026-08-30 (held to each Schema by tools/check_fields.py)
  - id: readthedocs-ecco-v4-heat-budget-closure
    resource: https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Heat_budget_closure.html
    title: "ECCO v4 Python tutorial: heat budget closure notebook"
verified:
  - { by: process:cmr-shortname-sweep, at: 2026-08-30T20:07:19Z }
  - { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
---

# Sea surface height

Dynamic sea surface height and model sea level anomaly from the ECCO
V4r4 ocean and sea-ice state estimate, on the native llc90 grid and the
interpolated 0.5 degree grid, monthly and daily means plus
instantaneous snapshots.[^podaac-landing] The snapshot collection's
`ETAN` provides the month-boundary states that form the z* scale factor
in property budgets.[^readthedocs-ecco-v4-heat-budget-closure] Sea surface height and ocean
bottom pressure are the two gridded V4r4 families that ship a corrected V4R4B
re-release alongside the original V4R4 collections; an analysis that
mixes the two releases folds the baseline correction into the signal
(the release-mixing gotcha below records the mechanism).[^cmr-sweep]

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

- `ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4`: native llc90, monthly mean. DOI: 10.5067/ECL5M-SSH44.
- `ECCO_L4_SSH_LLC0090GRID_DAILY_V4R4`: native llc90, daily mean. DOI: 10.5067/ECL5D-SSH44.
- `ECCO_L4_SSH_LLC0090GRID_SNAPSHOT_V4R4`: native llc90, instantaneous snapshots (budget bookends; ETAN for z*). DOI: 10.5067/ECL5S-SSH44.
- `ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4B`: native llc90, monthly mean, corrected V4R4B release. DOI: 10.5067/ECL5M-SSH4B.
- `ECCO_L4_SSH_LLC0090GRID_DAILY_V4R4B`: native llc90, daily mean, corrected V4R4B release. DOI: 10.5067/ECL5D-SSH4B.
- `ECCO_L4_SSH_05DEG_MONTHLY_V4R4`: 0.5 degree interpolated, monthly mean; display and comparison, not budgets. DOI: 10.5067/ECG5M-SSH44.
- `ECCO_L4_SSH_05DEG_DAILY_V4R4`: 0.5 degree interpolated, daily mean; display and comparison, not budgets. DOI: 10.5067/ECG5D-SSH44.
- `ECCO_L4_SSH_05DEG_MONTHLY_V4R4B`: 0.5 degree interpolated, monthly mean, corrected V4R4B release. DOI: 10.5067/ECG5M-SSH4B.
- `ECCO_L4_SSH_05DEG_DAILY_V4R4B`: 0.5 degree interpolated, daily mean, corrected V4R4B release. DOI: 10.5067/ECG5D-SSH4B.

# Known issues

Mixing V4R4 and V4R4B collections in one analysis conflates the
baseline correction with the geophysical signal
([ecco-release-mixing](../../gotchas/ecco-release-mixing.md)).

[^podaac-landing]: PO.DAAC dataset landing page
[^cmr-sweep]: CMR ShortName sweep, tools/verify_cmr.py
[^family-manifest]: ECCO V4r4 family manifest, tools/ecco_v4r4_families.yaml
[^readthedocs-ecco-v4-heat-budget-closure]: ECCO v4 Python tutorial: heat budget closure notebook
