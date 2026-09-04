---
type: Data Collection
title: Ocean and sea-ice surface freshwater fluxes
description: "The surface freshwater and salt flux family of the V4r4 estimate: SFLUX and oceFWflx plus forcing components; the salt-budget surface forcing."
tags: [ecco, v4r4, surface-water, salinity-density]
resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_FRESH_FLUX_LLC0090GRID_MONTHLY_V4R4
status: stable
generated: { by: claude-code/fable-5, at: 2026-08-30T20:15:00Z }
stale_after: 2027-01-04
sources:
  - id: podaac-landing
    resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_FRESH_FLUX_LLC0090GRID_MONTHLY_V4R4
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

# Ocean and sea-ice surface freshwater fluxes

Ocean and sea-ice surface freshwater fluxes from the ECCO V4r4 estimate
on the native llc90 grid and the interpolated 0.5 degree grid, monthly
and daily means.[^podaac-landing] `SFLUX` is the salt-budget surface
forcing term; EXF and sea-ice forcing components ride in this family,
enumerated at granule verification 2026-08-30 (Schema
below).[^family-manifest] In the volume budget there is no freshwater
forcing term at all: `WVELMASS` at the surface already carries the
freshwater volume flux, and adding `oceFWflx` as a forcing term
double-counts it (measured in
[ecco-volume-budget](../../recipes/ecco-volume-budget.md)).

# Schema

| Variable | Units | Grid point | Description | Provenance |
|---|---|---|---|---|
| `SFLUX` | g m-2 s-1 | c center | Total salt flux into the ocean surface; salt-budget forcing term | granule-verified 2026-08-30 |
| `oceFWflx` | kg m-2 s-1 | c center | Net surface freshwater flux (precipitation minus evaporation plus runoff) | granule-verified 2026-08-30 |
| `EXFempmr` | m s-1 | c center | Open ocean net surface freshwater flux from precipitation, evaporation, and runoff | granule-verified 2026-08-30 |
| `EXFevap` | m s-1 | c center | Open ocean evaporation rate | granule-verified 2026-08-30 |
| `EXFpreci` | m s-1 | c center | Precipitation rate | granule-verified 2026-08-30 |
| `EXFroff` | m s-1 | c center | River runoff | granule-verified 2026-08-30 |
| `SIacSubl` | kg m-2 s-1 | c center | Freshwater flux to the atmosphere from sublimation-deposition of snow or ice | granule-verified 2026-08-30 |
| `SIatmFW` | kg m-2 s-1 | c center | Net freshwater flux into the open ocean, sea-ice, and snow | granule-verified 2026-08-30 |
| `SIfwThru` | kg m-2 s-1 | c center | Precipitation through sea-ice | granule-verified 2026-08-30 |
| `SIrsSubl` | kg m-2 s-1 | c center | Residual sublimation freshwater flux | granule-verified 2026-08-30 |
| `SIsnPrcp` | kg m-2 s-1 | c center | Snow precipitation on sea-ice | granule-verified 2026-08-30 |

# Variants

All four ShortNames verified in CMR by the 2026-08-30 sweep.[^cmr-sweep]

- `ECCO_L4_FRESH_FLUX_LLC0090GRID_MONTHLY_V4R4`: native llc90, monthly mean. DOI: 10.5067/ECL5M-FRE44.
- `ECCO_L4_FRESH_FLUX_LLC0090GRID_DAILY_V4R4`: native llc90, daily mean. DOI: 10.5067/ECL5D-FRE44.
- `ECCO_L4_FRESH_FLUX_05DEG_MONTHLY_V4R4`: 0.5 degree interpolated, monthly mean; display and comparison, not budgets. DOI: 10.5067/ECG5M-FRE44.
- `ECCO_L4_FRESH_FLUX_05DEG_DAILY_V4R4`: 0.5 degree interpolated, daily mean; display and comparison, not budgets. DOI: 10.5067/ECG5D-FRE44.

# Known issues

Adding `oceFWflx` as a volume-budget forcing term double-counts the
freshwater flux already in `WVELMASS`; the closure detects it
([ecco-volume-budget](../../recipes/ecco-volume-budget.md)).

[^podaac-landing]: PO.DAAC dataset landing page
[^cmr-sweep]: CMR ShortName sweep, tools/verify_cmr.py
[^family-manifest]: ECCO V4r4 family manifest, tools/ecco_v4r4_families.yaml
