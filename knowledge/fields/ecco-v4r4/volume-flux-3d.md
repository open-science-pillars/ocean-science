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
  - id: variable-catalog
    resource: https://github.com/open-science-pillars/ocean-science/blob/main/skills/ecco/references/variable-catalog.md
    title: OSP ECCO variable catalog (sweep of 2026-07-04)
    author: human:PaulMRamirez
verified:
  - { by: process:cmr-shortname-sweep, at: 2026-08-30T20:07:19Z }
  - { by: human:PaulMRamirez, at: 2026-08-30T20:30:00Z }
---

# Ocean three-dimensional volume fluxes

Ocean three-dimensional volume fluxes from the ECCO V4r4 estimate on the
native llc90 grid, monthly and daily means: the mass-weighted transports
that transport analyses and the volume budget
consume.[^podaac-landing][^variable-catalog] Flux variables with a MASS
suffix already carry the partial-cell factor hFac; applying it a second
time double-counts it.[^variable-catalog] `WVELMASS` at the surface
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

- `ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_MONTHLY_V4R4`: native llc90, monthly mean.
- `ECCO_L4_OCEAN_3D_VOLUME_FLUX_LLC0090GRID_DAILY_V4R4`: native llc90, daily mean.

# Known issues

Budgets built from these fluxes close only on the native grid
([ecco-native-vs-regridded](../../gotchas/ecco-native-vs-regridded.md));
the surface freshwater double-count trap is recorded in
[ecco-volume-budget](../../recipes/ecco-volume-budget.md).

[^podaac-landing]: PO.DAAC dataset landing page
[^cmr-sweep]: CMR ShortName sweep, tools/verify_cmr.py
[^variable-catalog]: OSP ECCO variable catalog (sweep of 2026-07-04)
