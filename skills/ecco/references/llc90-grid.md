# The LLC90 native grid: procedure and pointers

Reference for the ecco skill. This file is procedure over the knowledge
concepts; the grid facts (tile layout and dimensions, the geometry
variable inventory, which variables already carry the partial-cell
fraction, which collections do not conserve) are read from the concepts
named below, never from here.

## Where the facts live

- Tile layout, dimensions, and the curvilinear coordinates:
  `knowledge/podaac/datasets/ecco-v4r4.md` (Structure).
- The geometry collection and its variable inventory (cell centers and
  corners, areas, edge lengths, layer spacing, the partial-cell
  fractions, the masks, the rotation angle fields), with the note that
  the horizontal and vertical coordinates arrive as xarray coordinates
  rather than data variables:
  `knowledge/podaac/fields/ecco-v4r4/geometry.md`.
- Which variables are already cell-integrated (the MASS suffix, the
  flux diagnostics) and the double-count trap:
  `knowledge/podaac/gotchas/ecco-velmass-hfac-double-count.md`.
- Why budgets and transports stay on the native grid, with the
  evidence: `knowledge/podaac/gotchas/ecco-native-vs-regridded.md`.
- Grid-relative velocity components on the rotated tiles:
  `knowledge/podaac/gotchas/ecco-vector-orientation.md` (a
  draft, voiced as unverified).
- The grid method that generalizes across models (C-grid staggering,
  cell geometry as data, xgcm, scalar versus vector regridding): the
  ocean-grids skill.

## Procedure

1. Identify the grid from the dataset concept before touching data:
   dimensions `(time, tile, k, j, i)` with 2D `XC, YC` per tile mean
   curvilinear; nothing about `(j, i)` is longitude-latitude, and
   treating a tile as a regular grid is the foundational mistake.
2. Load the geometry collection first and merge it into every native
   dataset (`xarray.merge`); take the variable names from the geometry
   concept, and read its coordinates as coordinates (code that iterates
   `data_vars` looking for them finds nothing).
3. Volume element: cell area times layer spacing times the partial-cell
   fraction at the cell center, per the geometry concept. Never apply
   the fraction a second time to a variable the double-count gotcha
   lists as already carrying it.
4. Staggering: scalars at cell centers, u on western faces, v on
   southern faces, w on lower faces (C-grid, per ocean-grids). Face
   transports use the face value times the matching edge length and
   layer spacing directly; a center-point velocity needs xgcm
   interpolation.
5. Tile seams: build the xgcm Grid with `ecco_v4_py.get_llc_grid(ds)`
   and difference or interpolate through it. Hand-rolled `np.diff`
   across `(j, i)` produces garbage at every seam that looks fine in
   tile interiors; within-tile interior cells need no seam operators,
   which is why pointwise closure fixtures use them.
6. Vectors: on the rotated tiles, model u and v are not geographic east
   and north. Rotate with the geometry concept's angle fields before any
   map or regridding, or compute transports in grid-native directions
   where the rotation cancels; the vector-orientation gotcha records
   which tiles rotate.
7. Plotting: never pcolormesh a tile array as if `(j, i)` were lon-lat;
   `ecco_v4_py.plot_proj_to_latlon_grid` resamples correctly and handles
   the cap. Regridding is for display and comparison only; the
   native-vs-regridded gotcha carries the evidence.
8. Sections: `ecco_v4_py.get_section_line_masks` (or
   `get_available_sections` for named sections) gives the W and S face
   masks; sum the MASS transports times face geometry over the masks,
   with no rotation step. The meridional-transport skill carries the
   method.
