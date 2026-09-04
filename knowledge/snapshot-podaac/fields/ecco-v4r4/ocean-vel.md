---
type: Data Collection
title: Ocean velocity
description: "The velocity family of the V4r4 estimate: UVEL, VVEL, and the vertical velocity WVEL on native and interpolated grids."
tags: [ecco, v4r4, ocean-circulation]
resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_OCEAN_VEL_LLC0090GRID_MONTHLY_V4R4
status: stable
generated: { by: claude-code/fable-5, at: 2026-08-30T20:15:00Z }
stale_after: 2027-01-04
sources:
  - id: podaac-landing
    resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_OCEAN_VEL_LLC0090GRID_MONTHLY_V4R4
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

# Ocean velocity

Ocean velocity from the ECCO V4r4 ocean and sea-ice state estimate on
the native llc90 grid and the interpolated 0.5 degree grid, monthly and
daily means.[^podaac-landing] This is the velocity ShortName family; the
OBP collections are ocean bottom pressure, a different product (the
naming confusion this distinction exists to prevent).[^cmr-sweep]
The interpolated collections carry east/north velocity components whose
exact variable names are confirmed at granule verification (manifest
note). Granule verification 2026-08-30: the native monthly granule
carries `WVEL` (vertical velocity), not `WVELMASS`; the mass-weighted
transports live in the volume-flux family (a catalog correction
recorded in the manifest).[^family-manifest]

# Schema

| Variable | Units | Grid point | Description | Provenance |
|---|---|---|---|---|
| `UVEL` | m s-1 | w face | Ocean velocity, model x component | granule-verified 2026-08-30 |
| `VVEL` | m s-1 | s face | Ocean velocity, model y component | granule-verified 2026-08-30 |
| `WVEL` | m s-1 | vertical face (k_l) | Vertical velocity | granule-verified 2026-08-30 |

# Variants

All four ShortNames verified in CMR by the 2026-08-30 sweep.[^cmr-sweep]

- `ECCO_L4_OCEAN_VEL_LLC0090GRID_MONTHLY_V4R4`: native llc90, monthly mean. DOI: 10.5067/ECL5M-OVE44.
- `ECCO_L4_OCEAN_VEL_LLC0090GRID_DAILY_V4R4`: native llc90, daily mean. DOI: 10.5067/ECL5D-OVE44.
- `ECCO_L4_OCEAN_VEL_05DEG_MONTHLY_V4R4`: 0.5 degree interpolated, monthly mean; display and comparison, not budgets. DOI: 10.5067/ECG5M-OVE44.
- `ECCO_L4_OCEAN_VEL_05DEG_DAILY_V4R4`: 0.5 degree interpolated, daily mean; display and comparison, not budgets. DOI: 10.5067/ECG5D-OVE44.

# Known issues

Native `UVEL` and `VVEL` are grid-relative components, not east and
north; rotation via the geometry's CS and SN comes before geographic
interpretation
([ecco-vector-orientation](../../gotchas/ecco-vector-orientation.md)).

[^podaac-landing]: PO.DAAC dataset landing page
[^cmr-sweep]: CMR ShortName sweep, tools/verify_cmr.py
[^family-manifest]: ECCO V4r4 family manifest, tools/ecco_v4r4_families.yaml
