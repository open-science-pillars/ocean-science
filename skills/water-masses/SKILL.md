---
name: water-masses
description: "Water mass identification: T-S diagrams, potential density surfaces, mode and deep waters, ventilation."
user-invocable: false
---

# water-masses

Background expertise for water mass analysis that respects its own
conventions. Authored in Session 8 per SPECIFICATION.md v0.5.1 §4.1
(v0.1 scope reconstructed from the description; flagged).

## Temperature and salinity are families, not single variables

Before any T-S work, establish which flavors are in hand: in-situ,
potential (theta), or Conservative Temperature; practical (PSS-78,
unitless) or Absolute Salinity (g/kg, TEOS-10). Model output is
typically potential temperature and practical salinity (ECCO: THETA,
SALT); modern observational products increasingly ship TEOS-10
variables. Mixing flavors on one diagram or density surface shifts
water-mass boundaries by tenths of a degree and a few hundredths in
salinity, silently. Convert deliberately (the gsw library implements
TEOS-10) and label axes with the exact variables used.

## Density surfaces and reference pressures

- Potential density is referenced: sigma0 (surface), sigma2 (2000 dbar),
  sigma4 (4000 dbar). Deep water-mass analysis on sigma0 misorders
  water columns (the classic AABW-NADW inversion artifact); use the
  reference appropriate to the depth range, and say which.
- Neutral density and TEOS-10 potential density differ enough at depth
  to move boundaries; consistency across a study matters more than the
  specific choice.
- Density from model T and S uses the model's own equation of state
  when budgets or stratification are in play (ECCO ships RHOAnoma and
  DRHODR in the density collection; recomputing with a different EOS
  creates phantom stratification differences).

## T-S diagrams

Volumetric census beats scatter: weight T-S bins by cell volume
(rA * drF * hFacC on native grids, per ocean-grids) so the diagram
shows where the water actually is, not where the grid points are.
Overlay density contours computed with the same EOS and reference as
the axes variables. Straight lines in T-S space are mixing lines;
curvature indicates more than two end members or non-mixing
transformation.

## Mode, intermediate, and deep waters

Water masses are identified by property extrema and thickness, not by
hard T-S boxes alone: mode waters as low-stratification thickness
maxima (low potential vorticity), intermediate waters commonly as
salinity minima (AAIW-type), deep and bottom waters by density class
with formation-region provenance. Fixed T-S class boundaries from the
literature are climatological conveniences; they drift between
products and decades, so state the boundary definition used and its
source rather than presenting class volumes as observations.

## Ventilation

Ventilation connects surface formation to interior properties: mixed
layer depth extremes set what outcrops (see mixed-layer), and
along-isopycnal spreading carries surface signatures into the interior.
Age and transit-time language requires a tracer or model diagnostic;
property-only inference ("this water looks young") is a hypothesis,
not a result.

## Must NOT

- Never mix temperature or salinity flavors on one diagram, surface,
  or comparison without explicit conversion.
- Never analyze deep water masses on sigma0.
- Never present an unweighted T-S scatter as a volumetric census.
- Never recompute density with a foreign EOS when the product ships
  its own and consistency matters.
- Never state fixed water-mass boundaries without naming their source
  and vintage.
