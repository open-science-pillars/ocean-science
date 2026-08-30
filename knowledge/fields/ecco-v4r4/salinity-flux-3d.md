---
type: Data Collection
title: Ocean three-dimensional salinity fluxes
description: "The salt-budget flux family of the V4r4 estimate: advective and diffusive salinity fluxes plus the salt-plume tendency, native grid only."
tags: [ecco, v4r4, salinity-density]
resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_OCEAN_3D_SALINITY_FLUX_LLC0090GRID_MONTHLY_V4R4
status: stable
generated: { by: claude-code/fable-5, at: 2026-08-30T20:15:00Z }
stale_after: 2027-01-04
sources:
  - id: podaac-landing
    resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_OCEAN_3D_SALINITY_FLUX_LLC0090GRID_MONTHLY_V4R4
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

# Ocean three-dimensional salinity fluxes

Ocean three-dimensional salinity fluxes from the ECCO V4r4 estimate on
the native llc90 grid, monthly and daily means: the advective and
diffusive salt-budget fluxes plus the three-dimensional salt-plume
tendency `oceSPtnd`.[^podaac-landing][^variable-catalog] The salt-budget
recipe consumes the monthly collection with the fresh-flux family and
the snapshot bookends ([ecco-salt-budget](../../recipes/ecco-salt-budget.md)).
No interpolated variant exists; this family is native-grid only
(manifest).

# Schema

| Variable | Units | Grid point | Description | Provenance |
|---|---|---|---|---|
| `ADVx_SLT` | 1e-3 m3 s-1 | w face | Advective salinity flux, model x | granule-verified 2026-08-30 |
| `ADVy_SLT` | 1e-3 m3 s-1 | s face | Advective salinity flux, model y | granule-verified 2026-08-30 |
| `ADVr_SLT` | 1e-3 m3 s-1 | vertical face | Advective salinity flux, vertical | granule-verified 2026-08-30 |
| `DFxE_SLT` | 1e-3 m3 s-1 | w face | Diffusive salinity flux, explicit, model x | granule-verified 2026-08-30 |
| `DFyE_SLT` | 1e-3 m3 s-1 | s face | Diffusive salinity flux, explicit, model y | granule-verified 2026-08-30 |
| `DFrE_SLT` | 1e-3 m3 s-1 | vertical face | Diffusive salinity flux, explicit, vertical | granule-verified 2026-08-30 |
| `DFrI_SLT` | 1e-3 m3 s-1 | vertical face | Diffusive salinity flux, implicit, vertical | granule-verified 2026-08-30 |
| `oceSPtnd` | g m-2 s-1 | c center | Salt tendency from the sea-ice salt plume | granule-verified 2026-08-30 |

# Variants

Both ShortNames verified in CMR by the 2026-08-30 sweep.[^cmr-sweep]

- `ECCO_L4_OCEAN_3D_SALINITY_FLUX_LLC0090GRID_MONTHLY_V4R4`: native llc90, monthly mean.
- `ECCO_L4_OCEAN_3D_SALINITY_FLUX_LLC0090GRID_DAILY_V4R4`: native llc90, daily mean.

# Known issues

Budgets built from these fluxes close only on the native grid
([ecco-native-vs-regridded](../../gotchas/ecco-native-vs-regridded.md)).

[^podaac-landing]: PO.DAAC dataset landing page
[^cmr-sweep]: CMR ShortName sweep, tools/verify_cmr.py
[^variable-catalog]: OSP ECCO variable catalog (sweep of 2026-07-04)
