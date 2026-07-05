# The LLC90 native grid

Reference for the ecco skill, per SPEC §4.2. Field
names marked "pending" are granule-verified during this session's access
test and the marks removed then; everything else follows the ECCO v4
release documentation and the ecco_v4_py tutorial conventions.

## Topology: lat-lon-cap, 13 tiles

ECCO v4r4 lives on the LLC90 grid: 13 tiles of 90 x 90 cells, 50 depth
levels. Tiles 0 to 5 cover the Southern Ocean through the Atlantic and
Indian sectors on a quasi-lat-lon layout; tile 6 is the Arctic cap;
tiles 7 to 12 cover the Pacific sector with axes ROTATED roughly 90
degrees relative to tiles 0 to 5. Data arrives with dimensions
`(time, tile, k, j, i)` (scalars) and curvilinear 2D coordinates
`XC, YC` per tile. Nothing about `(j, i)` is longitude-latitude; treating
tiles as regular grids is the foundational llc90 mistake.

## Geometry fields (from ECCO_L4_GEOMETRY_LLC0090GRID_V4R4)

- Cell centers `XC, YC`; corners `XG, YG`; cell areas `rA` (m^2).
- Edge lengths `dxG, dyG`; vertical spacing `drF` (m); depths `Depth`,
  level coordinates `Z, Zl, Zu` (negative down, 50 levels).
- **Partial cells:** `hFacC, hFacW, hFacS` give the wet fraction of each
  cell (0 to 1). Volume integrals use `rA * drF * hFacC`, never
  `rA * drF`; omitting hFac biases every budget and inventory near
  topography.
- Land masks `maskC, maskW, maskS` ship in the geometry granule
  (granule-verified 2026-07-04).
- Vector rotation fields `CS`, `SN` (cos/sin of the local grid angle,
  granule-verified 2026-07-04) for rotating model u/v to geographic
  east/north.
- Nuance: `XC, YC, XG, YG` and the vertical axes arrive as xarray
  COORDINATES on the geometry dataset, not data variables; code that
  iterates `data_vars` looking for them finds nothing.

## C-grid staggering

Arakawa C-grid: scalars (THETA, SALT) at cell centers; `UVEL`/`UVELMASS`
on western cell faces; `VVEL`/`VVELMASS` on southern faces; `WVELMASS`
on lower faces. Consequences:

1. Center-point values of velocity require interpolation (xgcm `interp`),
   and transports across faces use the face values directly:
   `UVELMASS * dyG * drF` is the volume transport through the western
   face (hFac is already inside UVELMASS; that is what the MASS suffix
   means, and double-applying hFac is a classic budget bug).
2. **On tiles 7 to 12, model u and v are not geographic east and north.**
   Any map of "zonal velocity" built from raw UVEL is wrong in the
   Pacific sector; rotate with the grid-angle fields or compute
   transports in grid-native directions where rotation cancels.

## xgcm and tile connectivity

Differencing and interpolating across tile boundaries requires the tile
connectivity map; `ecco_v4_py.get_llc_grid(ds)` builds the xgcm Grid
with the llc face connections, and `xgcm.Grid.diff`/`interp` then respect
the topology (including the Arctic cap's rotated neighbors). Hand-rolled
`np.diff` across `(j, i)` silently produces garbage at every tile seam;
budget divergences built that way fail closure at the seams while looking
fine in tile interiors.

## Plotting and regridding

- Maps: never pcolormesh a tile array as if `(j, i)` were lon-lat; use
  `ecco_v4_py.plot_proj_to_latlon_grid` (resamples correctly, handles
  the cap) or explicit resampling to a regular grid for display.
- Regridding is for DISPLAY and comparison only. Budgets and transports
  are computed on the native grid; the interpolated 0.5 degree ECCO
  product does not conserve, and budget closure fails on it by
  construction (the ecco-native-vs-regridded gotcha carries the
  evidence).

## Sections and transports

Meridional/section transports use face transports with section masks:
`ecco_v4_py.get_section_line_masks` (or `get_available_sections` for
named sections) produces the W/S face masks; summing
`UVELMASS * dyG * drF` and `VVELMASS * dxG * drF` over masked faces
gives the section transport without any rotation step.
