---
name: water-masses
description: "Water mass identification: T-S diagrams, potential density surfaces, mode and deep waters, ventilation."
user-invocable: false
---

# water-masses

Background expertise for water mass analysis that respects its own
conventions. This file carries the PROCEDURE and the hard refusals. The
product-specific facts (which variable is which temperature or salinity
flavor, which density fields a product ships from its own equation of
state, the source and vintage of any water-mass class boundary) do NOT
live here: they are read from the knowledge bundle per analysis.

## Consult the bundle for this product and analysis

Before any T-S work on a specific product, DISCOVER and read the
applicable knowledge concepts; do not work from a remembered variable
list. Glob and grep `knowledge/datasets/`, `knowledge/gotchas/`, and
`knowledge/conventions/` by product name and by topic (temperature,
salinity, density, EOS, water mass), read the matches, and restate
(citing each by path) what the product fixes about the plan: which
variables carry potential temperature and practical salinity (or whether
the product ships TEOS-10 Conservative Temperature and Absolute
Salinity), which density fields it provides from its own equation of
state, and any product gotcha that constrains density or stratification
work. A concept added since you last ran is found this way. Nothing
about a specific product is carried in this file.

## Temperature and salinity are families, not single variables (method)

Before any T-S work, establish which flavors are in hand: in-situ,
potential (theta), or Conservative Temperature; practical (PSS-78,
unitless) or Absolute Salinity (g/kg, TEOS-10). Model output is commonly
potential temperature and practical salinity; modern observational
products increasingly ship TEOS-10 variables; which variable is which
flavor for the product in hand is read from the bundle, not assumed.
Mixing flavors on one diagram or density surface shifts water-mass
boundaries by tenths of a degree and a few hundredths in salinity,
silently. Convert deliberately (the gsw library implements TEOS-10) and
label axes with the exact variables used.

## Density surfaces and reference pressures (method)

- Potential density is referenced: sigma0 (surface), sigma2 (2000 dbar),
  sigma4 (4000 dbar). Deep water-mass analysis on sigma0 misorders
  water columns (the classic AABW-NADW inversion artifact); use the
  reference appropriate to the depth range, and say which.
- Neutral density and TEOS-10 potential density differ enough at depth
  to move boundaries; consistency across a study matters more than the
  specific choice.
- Density from model T and S must use the product's own equation of
  state when budgets or stratification are in play; recomputing with a
  foreign EOS creates phantom stratification. Which density fields a
  product ships from its own EOS, and the gotcha that recomputing
  produces, are dataset facts read from the bundle (via the consult
  step), not carried here.

## T-S diagrams (method)

Volumetric census beats scatter: weight T-S bins by cell volume
(rA * drF * hFacC on native grids, per ocean-grids) so the diagram
shows where the water actually is, not where the grid points are.
Overlay density contours computed with the same EOS and reference as
the axes variables. Straight lines in T-S space are mixing lines;
curvature indicates more than two end members or non-mixing
transformation.

## Mode, intermediate, and deep waters (method)

Water masses are identified by property extrema and thickness, not by
hard T-S boxes alone: mode waters as low-stratification thickness
maxima (low potential vorticity), intermediate waters commonly as
salinity minima (AAIW-type), deep and bottom waters by density class
with formation-region provenance. Fixed T-S class boundaries from the
literature are climatological conveniences; they drift between
products and decades, so state the boundary definition used and its
source rather than presenting class volumes as observations. The
specific boundary values for a given product or study are read from the
bundle or the cited literature, never inlined here.

## Ventilation (method)

Ventilation connects surface formation to interior properties: mixed
layer depth extremes set what outcrops (see mixed-layer), and
along-isopycnal spreading carries surface signatures into the interior.
Age and transit-time language requires a tracer or model diagnostic;
property-only inference ("this water looks young") is a hypothesis,
not a result.

## Hard refusals (invariant, universal; fire without consulting anything)

- Never mix temperature or salinity flavors on one diagram, surface,
  or comparison without explicit conversion.
- Never analyze deep water masses on sigma0.
- Never present an unweighted T-S scatter as a volumetric census.
- Never recompute density with a foreign EOS when the product ships
  its own and consistency matters.
- Never state fixed water-mass boundaries without naming their source
  and vintage.
