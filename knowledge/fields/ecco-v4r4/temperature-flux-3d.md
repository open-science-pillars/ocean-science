---
type: Data Collection
title: Ocean three-dimensional potential temperature fluxes
description: "The heat-budget flux family of the V4r4 estimate: advective and diffusive potential temperature fluxes on the native grid only."
tags: [ecco, v4r4, ocean-heat-budget]
resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_MONTHLY_V4R4
status: stable
generated: { by: claude-code/fable-5, at: 2026-08-30T20:15:00Z }
stale_after: 2027-01-04
sources:
  - id: podaac-landing
    resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_MONTHLY_V4R4
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

# Ocean three-dimensional potential temperature fluxes

Ocean three-dimensional potential temperature fluxes from the ECCO V4r4
estimate on the native llc90 grid, monthly and daily means: the
advective and diffusive heat-budget fluxes.[^podaac-landing][^variable-catalog]
The heat-budget recipe consumes the monthly collection together with the
heat-flux family and the snapshot bookends
([ecco-heat-budget](../../recipes/ecco-heat-budget.md)). No interpolated
variant exists; this family is native-grid only (manifest).

# Schema

| Variable | Units | Grid point | Description | Provenance |
|---|---|---|---|---|
| `ADVx_TH` | degree_C m3 s-1 | w face | Advective potential temperature flux, model x | granule-verified 2026-08-30 |
| `ADVy_TH` | degree_C m3 s-1 | s face | Advective potential temperature flux, model y | granule-verified 2026-08-30 |
| `ADVr_TH` | degree_C m3 s-1 | vertical face | Advective potential temperature flux, vertical | granule-verified 2026-08-30 |
| `DFxE_TH` | degree_C m3 s-1 | w face | Diffusive potential temperature flux, explicit, model x | granule-verified 2026-08-30 |
| `DFyE_TH` | degree_C m3 s-1 | s face | Diffusive potential temperature flux, explicit, model y | granule-verified 2026-08-30 |
| `DFrE_TH` | degree_C m3 s-1 | vertical face | Diffusive potential temperature flux, explicit, vertical | granule-verified 2026-08-30 |
| `DFrI_TH` | degree_C m3 s-1 | vertical face | Diffusive potential temperature flux, implicit, vertical | granule-verified 2026-08-30 |

# Variants

Both ShortNames verified in CMR by the 2026-08-30 sweep.[^cmr-sweep]

- `ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_MONTHLY_V4R4`: native llc90, monthly mean.
- `ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_DAILY_V4R4`: native llc90, daily mean.

# Known issues

Budgets built from these fluxes close only on the native grid
([ecco-native-vs-regridded](../../gotchas/ecco-native-vs-regridded.md)).

[^podaac-landing]: PO.DAAC dataset landing page
[^cmr-sweep]: CMR ShortName sweep, tools/verify_cmr.py
[^variable-catalog]: OSP ECCO variable catalog (sweep of 2026-07-04)
