---
name: meridional-transport
description: Meridional heat, volume, freshwater transport: section masks, overturning and gyre decomposition, RAPID comparison at 26.5N.
user-invocable: false
---

# meridional-transport

Background expertise for meridional transports that are computed
natively and framed honestly. Authored in Session 7 per SPECIFICATION.md
v0.5.1 §4.1 (v0.1 scope reconstructed from the description and the ecco
references; flagged). Expected values and spreads live in recipe
concepts; grid mechanics live in ocean-grids and the llc90 reference.

## Scope: a latitude line without a basin mask is the full circle

Section machinery given only a latitude computes the ENTIRE latitude
circle, all basins. Basin-scoped transports (the Atlantic for any RAPID
comparison) require the basin mask explicitly, and per-basin values sum
to the circle total (verified on ECCO 2010: Atlantic 0.666 + Pacific
0.430 + Indian 0.002 = 1.098 PW at 26.5N). Quoting a full-circle number
against a single-basin observation is a scope error that looks
plausible; the recipe concept records both scopes with anchors.

## Sections are masks, not index rows

On any curvilinear grid, a latitude circle crosses cells irregularly; a
section is a set of cell FACES with signs, not a `j = const` slice.
`ecco_v4_py.get_section_line_masks` (and `get_available_sections` for
named straits) produces the west- and south-face masks; transports sum
face fluxes times face geometry over those masks. Grid-native face
directions make rotation unnecessary in the sum (llc90 reference).

## Volume, heat, freshwater

- **Volume (Sv):** sum of `UVELMASS * dyG * drF` and
  `VVELMASS * dxG * drF` over the masked faces; the MASS variables
  already carry hFac and bolus is separate (below).
- **Heat (PW):** prefer the model's advective heat-flux diagnostics
  (`ADVx_TH`, `ADVy_TH` for ECCO) summed over the section, times
  rho0 * c_p on the temperature flux: these capture exactly what the
  model transported, including sub-monthly covariance that
  reconstructed v-times-theta from monthly means misses. **A heat
  transport is physically well defined only across a section with zero
  net mass transport**; where net mass transport is nonzero, the number
  is a temperature transport relative to a stated reference, and the
  reference must be stated.
- **Freshwater (Sv):** same structure with salt fluxes and a stated
  reference salinity; the reference-dependence caveat applies
  identically.

## Total means Eulerian plus bolus

In eddy-parameterized models the tracer transport includes the bolus
(GM) component; ECCO ships it as its own product (UVELSTAR family).
Eulerian-only transport labeled as total is a systematic bias; the
flux diagnostics (ADV*_TH) already include everything the model did,
which is another reason to prefer them for heat.

## Overturning and gyre decomposition

Zonally integrate meridional transport in depth space and cumulate
vertically for the overturning streamfunction (AMOC strength is its
maximum at the section, in Sv). Decompose section transport into
overturning (zonal-mean velocity times zonal-mean property) and gyre
(deviation) components to attribute mechanisms; on depth surfaces this
decomposition is convention-laden near western boundaries, so name the
convention used.

## The RAPID comparison at 26.5N

The RAPID-MOCHA array at 26.5N observes AMOC transport and MHT
continuously since April 2004: the standard ground truth for Atlantic
sections. The comparison discipline: compute the model section at
26.5N, compare the mean and variability against the recipe concept
`knowledge/recipes/ecco-mht-26n.md`, which carries the expected range,
the expected-uncertainty (the RAPID-comparison spread), and validation
provenance. The recipe is the authority; this skill carries no
expected ranges or spreads of its own (the basin values quoted under
Scope are the recipe's anchors, cited for the sum identity).
Time-sampling matters in the comparison: a single
year's mean sits inside a wider envelope than a multi-year mean, and
ECCO's 1992-2017 window overlaps RAPID only from 2004.

## Must NOT

- Never hardcode an expected transport range or spread; read the
  recipe concept and cite it.
- Never compute transports on regridded fields (ocean-grids rule;
  native faces only).
- Never slice `j = const` as a section on a curvilinear grid.
- Never quote a heat transport across a mass-unbalanced section
  without stating the reference temperature.
- Never label Eulerian-only transport as total in an
  eddy-parameterized model.
- Never compare a model mean against RAPID without matching the
  overlap period or saying the periods differ.
