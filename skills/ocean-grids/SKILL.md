---
name: ocean-grids
description: "Ocean model grids: Arakawa C-grid, LLC tiles, cell geometry, xgcm, scalar vs vector regridding rules."
user-invocable: false
---

# ocean-grids

Background expertise for working on ocean model grids without silent
geometry errors. This skill carries the grid METHOD that generalizes
across ocean models; it does not carry any product's grid facts,
variable names, or conservation caveats. ECCO llc90 specifics live in
the knowledge bundle's ECCO concepts, listed by the ecco skill, whose
grid reference is the procedure over them.

## Consult the bundle for product-specific facts

When an analysis targets a specific product (ECCO, or another GCM
output), consult installed knowledge concepts first, as the core
`consult-knowledge` skill sets out, by product name, variable, and grid
topic; read the matches, restate what each changes about the plan, and
cite it by path; do not carry those facts back into this skill. Which
of a product's variables are already cell-integrated, which collections
conserve, and the product's native grid layout are all read from the
product's concepts (for ECCO: the dataset concept, the geometry family
concept, and the hFac double-count and native-vs-regridded gotchas, all
listed by the ecco skill), never from an inlined list here. A concept
added since you last ran is found this way.

The refusal of a budget or transport on regridded fields is the ecco
skill's, which loads on every ECCO task; this skill supplies the method
reason (below) and the native-grid path offered in its place. The hard
refusals at the end are this skill's own grid-method gates.

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

Areas, edge lengths, layer thicknesses, and partial-cell fractions are
data, not derivables, on any non-regular grid; read them from the
model's own metric fields. Weights for means come from the geometry
fields, and vertical integrals include the partial-cell fraction. A
variable that is already cell-integrated must not have the cell factor
applied a second time (double-counting the partial cell is a standard
budget bug); which of a given product's variables are already
cell-integrated is a product fact, read from that product's concepts
(for ECCO, the geometry and flux family concepts and the hFac
double-count gotcha), not assumed here.

## xgcm

xgcm encodes the staggering: a `Grid` object with axes (X, Y, Z), shift
positions (center, left, right), and metrics. `grid.diff` and
`grid.interp` respect the topology, including periodic axes and, with
face-connection maps, multi-tile layouts (for ECCO,
`ecco_v4_py.get_llc_grid` builds it; the ecco skill's grid reference
carries the procedure). The failure mode it prevents: numpy operations across index
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
- **Transports and budgets: never regridded (method reason).** Compute
  on the native grid, integrate to the target quantity (a section
  transport, a basin budget), and present the integrated result.
  Interpolated fields do not conserve, so a budget or transport
  assembled from regridded fields is wrong by construction. The
  refusal itself is the ecco skill's; the product-specific evidence and
  the exact non-conserving collections live in that product's gotcha
  concept (for ECCO, `gotchas/ecco-native-vs-regridded.md`), consulted
  and cited in the refusal rather than restated here.

## Hard refusals

Each fires without consulting anything: invariant across products and
time, refusal-shaped, and wrong or unsafe regardless of dataset.

- Never treat curvilinear indices as latitude and longitude.
- Never compute weights from cos(lat) when the grid provides cell areas.
- Never difference across tile or fold seams without topology-aware
  operators.
- Never regrid vectors without rotating to geographic components first.
- Never assemble a budget or transport from regridded fields; the
  refusal is the ecco skill's, and this skill's part is the
  native-grid path offered in its place.
