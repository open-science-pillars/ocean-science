---
type: Data Collection
title: Grid geometry parameters
description: "The llc90 and 0.5 degree grid geometry of the V4r4 estimate: areas, edge lengths, partial cells, masks, rotation, and bathymetry; the static granule merged into every native-grid analysis."
tags: [ecco, v4r4, model-geometry]
resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_GEOMETRY_LLC0090GRID_V4R4
status: stable
generated: { by: claude-code/fable-5, at: 2026-08-30T20:05:00Z }
stale_after: 2027-01-04
sources:
  - id: podaac-landing
    resource: https://podaac.jpl.nasa.gov/dataset/ECCO_L4_GEOMETRY_LLC0090GRID_V4R4
    title: PO.DAAC dataset landing page
  - id: cmr-sweep
    resource: all ECCO_L4_*V4R4* collections in CMR (provider POCLOUD)
    title: CMR ShortName sweep, tools/verify_cmr.py
  - id: cmr-granule
    resource: https://cmr.earthdata.nasa.gov/search/granules.umm_json?short_name=ECCO_L4_GEOMETRY_LLC0090GRID_V4R4
    title: "CMR granule record for the native collection: one granule, GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc (queried 2026-09-04)"
  - id: tut-grid-params
    resource: https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Loading_the_ECCOv4_native_model_grid_parameters.html
    title: "ECCO v4 Python Tutorial: Loading the ECCOv4 native model grid parameters (the opened geometry dataset, its coordinates and data variables)"
  - id: tut-load-native
    resource: https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Loading_the_ECCOv4_state_estimate_fields_on_the_native_model_grid.html
    title: "ECCO v4 Python Tutorial: Loading the ECCOv4 state estimate fields on the native model grid (combining datasets with xarray.merge)"
  - id: static-gotcha
    resource: ../../gotchas/ecco-access-static-collections.md
    title: "The static-collection access gotcha: ecco_access 0.3.1 and the earthaccess route"
verified:
  - { by: process:cmr-shortname-sweep, at: 2026-08-30T20:07:19Z }
  - { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
---

# Grid geometry parameters

Geometric parameters for the lat-lon-cap 90 (llc90) native model grid of
the ECCO V4r4 ocean and sea-ice state estimate: areas and lengths of
grid cell sides, horizontal and vertical coordinates of cell centers and
corners, grid rotation angles, and global domain geometry including
bathymetry and land/ocean masks.[^podaac-landing] The native collection
is one static granule (`GRID_GEOMETRY_ECCO_V4r4_native_llc0090.nc`,
about 8.6 MB), granule-verified 2026-07-04,[^cmr-granule] and is merged
into every native-grid dataset before analysis;[^tut-load-native] XC,
YC, XG, YG, Z, Zl, Zu, and Zp1 arrive as coordinates, not data
variables.[^tut-grid-params] Static collections are fetched via
earthaccess rather than ecco_access
([ecco-access-static-collections](../../gotchas/ecco-access-static-collections.md)).[^static-gotcha]
Units and grid placements below are confirmed against granule
attributes (granule verification 2026-08-30).

# Schema

| Variable | Units | Grid point | Description | Provenance |
|---|---|---|---|---|
| `rA` | m2 | c center | Tracer cell area | granule-verified 2026-07-04 |
| `rAw` | m2 | w face | West-face cell area | granule-verified 2026-07-04 |
| `rAs` | m2 | s face | South-face cell area | granule-verified 2026-07-04 |
| `rAz` | m2 | z corner | Corner (vorticity) cell area | granule-verified 2026-07-04 |
| `dxG` | m | s face | Cell side length in x | granule-verified 2026-08-30 |
| `dyG` | m | w face | Cell side length in y | granule-verified 2026-08-30 |
| `dxC` | m | w face | Center-to-center separation in x | granule-verified 2026-08-30 |
| `dyC` | m | s face | Center-to-center separation in y | granule-verified 2026-08-30 |
| `drF` | m | c center (vertical) | Cell thickness at centers | granule-verified 2026-07-04 |
| `drC` | m | vertical (k_p1) | Center-to-center vertical separation | granule-verified 2026-08-30 |
| `hFacC` | 1 | c center | Partial-cell open fraction at centers | granule-verified 2026-07-04 |
| `hFacW` | 1 | w face | Partial-cell open fraction at west faces | granule-verified 2026-07-04 |
| `hFacS` | 1 | s face | Partial-cell open fraction at south faces | granule-verified 2026-07-04 |
| `maskC` | (none) | c center | Land/ocean mask at centers | granule-verified 2026-08-30 |
| `maskW` | (none) | w face | Land/ocean mask at west faces | granule-verified 2026-08-30 |
| `maskS` | (none) | s face | Land/ocean mask at south faces | granule-verified 2026-08-30 |
| `CS` | 1 | c center | Grid rotation angle cosine | granule-verified 2026-07-04 |
| `SN` | 1 | c center | Grid rotation angle sine | granule-verified 2026-07-04 |
| `Depth` | m | c center | Bathymetry (ocean depth) | granule-verified 2026-07-04 |
| `PHrefC` | m2 s-2 | c center (vertical) | Reference hydrostatic pressure potential at centers | granule-verified 2026-07-04 |
| `PHrefF` | m2 s-2 | vertical face | Reference hydrostatic pressure potential at faces | granule-verified 2026-07-04 |

# Variants

Both ShortNames verified in CMR by the 2026-08-30 sweep.[^cmr-sweep]

- `ECCO_L4_GEOMETRY_LLC0090GRID_V4R4`: native llc90, static single granule. DOI: 10.5067/ECL5A-GRD44.
- `ECCO_L4_GEOMETRY_05DEG_V4R4`: 0.5 degree interpolated, static single granule; display and comparison, not budgets. DOI: 10.5067/ECG5A-GRD44.

[^podaac-landing]: PO.DAAC dataset landing page
[^cmr-sweep]: CMR ShortName sweep, tools/verify_cmr.py
[^cmr-granule]: CMR granule record for ECCO_L4_GEOMETRY_LLC0090GRID_V4R4 (queried 2026-09-04)
[^tut-grid-params]: ECCO v4 Python Tutorial: Loading the ECCOv4 native model grid parameters
[^tut-load-native]: ECCO v4 Python Tutorial: Loading the ECCOv4 state estimate fields on the native model grid
[^static-gotcha]: gotchas/ecco-access-static-collections.md
