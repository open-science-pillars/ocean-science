---
type: Data Collection
title: Ocean bottom pressure
description: "The OBP family of the V4r4 estimate: ocean bottom pressure and its anomaly, with snapshot bookends and a corrected V4R4B re-release for this family."
tags: [ecco, v4r4, ocean-pressure, geodesy]
resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_OBP_LLC0090GRID_MONTHLY_V4R4
status: stable
generated: { by: claude-code/fable-5, at: 2026-08-30T20:15:00Z }
stale_after: 2027-01-04
sources:
  - id: podaac-landing
    resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_OBP_LLC0090GRID_MONTHLY_V4R4
    title: PO.DAAC dataset landing page
  - id: cmr-sweep
    resource: all ECCO_L4_*V4R4* collections in CMR (provider POCLOUD)
    title: CMR ShortName sweep, tools/verify_cmr.py
  - id: family-manifest
    resource: ../../../../tools/ecco_v4r4_families.yaml
    title: ECCO V4r4 family manifest, the per-variable record of the granule verifications of 2026-07-04 and 2026-08-30 (held to each Schema by tools/check_fields.py)
verified:
  - { by: process:cmr-shortname-sweep, at: 2026-08-30T20:07:19Z }
  - { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
---

# Ocean bottom pressure

Ocean bottom pressure and model ocean bottom pressure anomaly from the
ECCO V4r4 estimate, on the native llc90 grid and the interpolated 0.5
degree grid, monthly and daily means plus instantaneous
snapshots.[^podaac-landing] Ocean bottom pressure and sea surface
height are the two gridded V4r4 families that ship a corrected V4R4B re-release
alongside the original V4R4 collections; an analysis that mixes the two
releases folds the baseline correction into the signal (the
release-mixing gotcha below records the
mechanism).[^cmr-sweep] This is the bottom-pressure ShortName
family; the OCEAN_VEL collections are velocity, a different product
(the naming confusion this distinction exists to
prevent).[^cmr-sweep]

# Schema

| Variable | Units | Grid point | Description | Provenance |
|---|---|---|---|---|
| `OBP` | m | c center | Ocean bottom pressure | granule-verified 2026-08-30 |
| `OBPGMAP` | m | c center | Ocean bottom pressure including the global mean atmospheric pressure contribution, per the user guide convention | granule-verified 2026-08-30 |
| `PHIBOT` | m2 s-2 | c center | Ocean hydrostatic bottom pressure anomaly | granule-verified 2026-08-30 |

# Variants

All nine ShortNames verified in CMR by the 2026-08-30 sweep.[^cmr-sweep]
V4R4B lines carry the corrected geodetic re-release for this family; a
series or comparison spanning V4R4 and V4R4B conflates the correction
with signal.

- `ECCO_L4_OBP_LLC0090GRID_MONTHLY_V4R4`: native llc90, monthly mean. DOI: 10.5067/ECL5M-OBP44.
- `ECCO_L4_OBP_LLC0090GRID_DAILY_V4R4`: native llc90, daily mean. DOI: 10.5067/ECL5D-OBP44.
- `ECCO_L4_OBP_LLC0090GRID_SNAPSHOT_V4R4`: native llc90, instantaneous snapshots. DOI: 10.5067/ECL5S-OBP44.
- `ECCO_L4_OBP_LLC0090GRID_MONTHLY_V4R4B`: native llc90, monthly mean, corrected V4R4B release. DOI: 10.5067/ECL5M-OBP4B.
- `ECCO_L4_OBP_LLC0090GRID_DAILY_V4R4B`: native llc90, daily mean, corrected V4R4B release. DOI: 10.5067/ECL5D-OBP4B.
- `ECCO_L4_OBP_05DEG_MONTHLY_V4R4`: 0.5 degree interpolated, monthly mean; display and comparison, not budgets. DOI: 10.5067/ECG5M-OBP44.
- `ECCO_L4_OBP_05DEG_DAILY_V4R4`: 0.5 degree interpolated, daily mean; display and comparison, not budgets. DOI: 10.5067/ECG5D-OBP44.
- `ECCO_L4_OBP_05DEG_MONTHLY_V4R4B`: 0.5 degree interpolated, monthly mean, corrected V4R4B release. DOI: 10.5067/ECG5M-OBP4B.
- `ECCO_L4_OBP_05DEG_DAILY_V4R4B`: 0.5 degree interpolated, daily mean, corrected V4R4B release. DOI: 10.5067/ECG5D-OBP4B.

# Known issues

Mixing V4R4 and V4R4B collections in one analysis conflates the
baseline correction with the geophysical signal
([ecco-release-mixing](../../gotchas/ecco-release-mixing.md)).

[^podaac-landing]: PO.DAAC dataset landing page
[^cmr-sweep]: CMR ShortName sweep, tools/verify_cmr.py
[^family-manifest]: ECCO V4r4 family manifest, tools/ecco_v4r4_families.yaml
