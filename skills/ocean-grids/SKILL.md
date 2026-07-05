---
name: ocean-grids
description: "Ocean model grids: Arakawa C-grid, LLC tiles, cell geometry, xgcm, scalar vs vector regridding rules."
user-invocable: false
---

# ocean-grids

Background expertise for working on ocean model grids without silent
geometry errors. ECCO llc90 specifics
live in `skills/ecco/references/llc90-grid.md`; this skill carries what
generalizes across ocean models.

## Identify the grid before touching the data

- 1D `lat`/`lon` coordinate variables: regular (or stretched) lat-lon;
  cos-lat weights are a valid approximation when no cell-area field
  exists.
- 2D coordinate arrays (`XC(j,i)`-style): curvilinear (tripolar,
  displaced-pole, lat-lon-cap); indices are NOT geographic axes, and
  cell geometry must come from the grid's own metric fields.
- Cell-connectivity or node lists: unstructured (FESOM, MPAS, ICON);
  nothing index-based generalizes, use the model's own tooling.

## Arakawa C-grid staggering

Most ocean GCMs (MITgcm/ECCO, NEMO, MOM) stagger on the C-grid: tracers
at cell centers, u on east-west faces, v on north-south faces, w on
top-bottom faces. Consequences that hold across models:

- Tracer-point velocity requires interpolation; face transports use the
  face values directly with the matching edge lengths.
- A dot product of raw u and v at "the same point" is a half-cell error.
- Divergences difference face fluxes; centered differences of
  interpolated fields do not conserve.

## Cell geometry

Areas (`rA` and friends), edge lengths (`dxG`, `dyG` families),
thicknesses (`drF`), and partial-cell fractions (`hFac*`) are data, not
derivables, on any non-regular grid. Weights for means come from the
geometry fields; vertical integrals include partial cells; flux
variables with a MASS suffix (or documented as cell-integrated) already
carry hFac, and applying it twice is a standard budget bug.

## xgcm

xgcm encodes the staggering: a `Grid` object with axes (X, Y, Z), shift
positions (center, left, right), and metrics. `grid.diff` and
`grid.interp` respect the topology, including periodic axes and, with
face-connection maps, multi-tile layouts (the llc90 reference documents
ECCO's). The failure mode it prevents: numpy operations across index
seams that look fine in the interior and corrupt every budget at tile
or fold boundaries (tripolar grids fold at the northern seam; LLC grids
rotate between tiles).

## Scalar vs vector regridding rules

- **Scalars for display or pointwise comparison:** bilinear or
  conservative regridding is fine; state the method.
- **Scalars for area integrals:** conservative regridding only, or
  better, integrate natively and regrid nothing.
- **Vectors:** rotate model (u, v) to geographic (east, north) with the
  grid's rotation fields BEFORE any regridding; regridding grid-relative
  components produces direction errors wherever the grid bends (the
  entire Arctic on most grids).
- **Transports and budgets: never regridded.** Compute on the native
  grid, integrate to the target quantity (a section transport, a basin
  budget), and present the integrated result. Interpolated fields do
  not conserve; the ecco bundle's native-vs-regridded gotcha carries
  the evidence for ECCO, and the rule is general.

## Must NOT

- Never treat curvilinear indices as latitude and longitude.
- Never compute weights from cos(lat) when the grid provides cell areas.
- Never difference across tile or fold seams without topology-aware
  operators.
- Never regrid vectors without rotating to geographic components first.
- Never compute budgets or transports on regridded fields.
- Never apply hFac to variables that already include it.
