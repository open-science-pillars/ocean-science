---
type: Data Collection
title: Ocean three-dimensional volume fluxes
description: "The mass-weighted transport family of the V4r4 estimate: UVELMASS, VVELMASS, WVELMASS, the transport-analysis and volume-budget inputs, native grid only."
tags: [ecco, v4r4, ocean-circulation]
resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_MONTHLY_V4R4
status: stable
generated: { by: claude-code/fable-5, at: 2026-08-30T20:15:00Z }
stale_after: 2027-01-04
sources:
  - id: podaac-landing
    resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_MONTHLY_V4R4
    title: PO.DAAC dataset landing page
  - id: cmr-sweep
    resource: all ECCO_L4_*V4R4* collections in CMR (provider POCLOUD)
    title: CMR ShortName sweep, tools/verify_cmr.py
  - id: family-manifest
    resource: ../../../../tools/ecco_v4r4_families.yaml
    title: ECCO V4r4 family manifest, the per-variable record of the granule verifications of 2026-07-04 and 2026-08-30 (held to each Schema by tools/check_fields.py)
  - id: tut-volume
    resource: https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Volume_budget_closure.html
    title: "ECCO v4 Python tutorial: global volume and sea level budget notebook"
verified:
  - { by: process:cmr-shortname-sweep, at: 2026-08-30T20:07:19Z }
  - { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
---

# Ocean three-dimensional volume fluxes

Ocean three-dimensional volume fluxes from the ECCO V4r4 estimate on the
native llc90 grid, monthly and daily means: the mass-weighted transports
that transport analyses and the volume budget
consume.[^podaac-landing][^family-manifest] Flux variables with a MASS
suffix already carry the partial-cell factor hFac; applying it a second
time double-counts it.[^tut-volume] `WVELMASS` at the surface
already carries the freshwater volume flux, so the volume budget closes
on transport convergence alone; a separate freshwater forcing term
double-counts (recorded with measurements in
[ecco-volume-budget](../../recipes/ecco-volume-budget.md)). No
interpolated variant exists; this family is native-grid only (manifest).

# Schema

| Variable | Units | Grid point | Description | Provenance |
|---|---|---|---|---|
| `UVELMASS` | m s-1 | w face | Mass-weighted velocity, model x component | granule-verified 2026-08-30 |
| `VVELMASS` | m s-1 m3 m-3 (granule attr as written) | s face | Mass-weighted velocity, model y component | granule-verified 2026-08-30 |
| `WVELMASS` | m s-1 | vertical face | Mass-weighted vertical velocity; carries the surface freshwater volume flux at k=0 | granule-verified 2026-08-30 |

# Variants

Both ShortNames verified in CMR by the 2026-08-30 sweep.[^cmr-sweep]

- `ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_MONTHLY_V4R4`: native llc90, monthly mean. DOI: 10.5067/ECL5M-3VF44.
- `ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_DAILY_V4R4`: native llc90, daily mean. DOI: 10.5067/ECL5D-3VF44.

# Known issues

Budgets built from these fluxes close only on the native grid
([ecco-native-vs-regridded](../../gotchas/ecco-native-vs-regridded.md));
the surface freshwater double-count trap is recorded in
[ecco-volume-budget](../../recipes/ecco-volume-budget.md).

[^podaac-landing]: PO.DAAC dataset landing page
[^cmr-sweep]: CMR ShortName sweep, tools/verify_cmr.py
[^family-manifest]: ECCO V4r4 family manifest, tools/ecco_v4r4_families.yaml
[^tut-volume]: ECCO v4 Python tutorial: global volume and sea level budget notebook
