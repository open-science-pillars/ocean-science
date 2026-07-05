---
name: mixed-layer
description: Mixed layer depth: density and temperature criteria, seasonal cycle, sensitivity to threshold choice.
user-invocable: false
---

# mixed-layer

Background expertise for mixed layer depth (MLD) work where the answer
depends on the definition. Authored in Session 8 per SPECIFICATION.md
v0.5.1 §4.1 (v0.1 scope reconstructed from the description; flagged).

## MLD is a criterion, not an observable

Every MLD number embeds a definition. The common families:

- **Density threshold:** depth where potential density exceeds its
  value at a reference depth (commonly 10 m) by a threshold; 0.03
  kg/m3 (de Boyer Montegut-style) and 0.125 kg/m3 (Levitus-style) are
  both widespread and can differ by tens of meters in weak
  stratification, by over 100 m in winter deep-mixing regions.
- **Temperature threshold:** 0.2 C or 0.5 C from the 10 m value;
  fails where salinity stratifies (barrier layers), reporting a
  mixed layer deeper than the density-mixed layer.
- **Gradient and hybrid criteria:** thresholds on the vertical
  derivative; sensitive to vertical resolution.

Model products may ship their own diagnostic (ECCO's MXLDEPTH row in
the variable catalog) computed with the model's internal criterion;
comparing it against an observational climatology computed with a
different criterion measures the criteria as much as the ocean.

## The comparison rule

MLD values are comparable only under the same criterion, reference
depth, AND input averaging: MLD computed from monthly-mean profiles is
biased shallow against the monthly mean of daily MLD (the mixing events
average out; winter biases reach tens of meters). State criterion,
reference depth, threshold, and averaging chain with every MLD number;
recompute rather than mix criteria when comparing products.

## Seasonal cycle and extremes

The seasonal cycle spans an order of magnitude (tens of meters in
summer to hundreds, locally thousands, in winter deep-convection
regions). Winter maximum MLD sets ventilation and mode-water formation
(see water-masses); summer minimum sets the biologically active layer.
Deep-convection winters are episodic: a climatological March MLD in
the Labrador Sea is not a typical March, it is an average over
convecting and non-convecting years. Barrier layers (salinity
stratification inside the isothermal layer) make temperature criteria
overestimate mixing depth in the tropics and subpolar fresh regions.

## Sensitivity discipline

Any MLD-derived conclusion carries a sensitivity check: recompute under
at least one alternative threshold (or criterion family) and report
whether the conclusion survives. Threshold sensitivity IS the
uncertainty statement for MLD (uncertainty-quantification's house rule
applies; there is no instrument error bar to quote for a definition).

## Must NOT

- Never report an MLD without criterion, threshold, reference depth,
  and input averaging.
- Never compare MLDs across products computed with different criteria
  as if they measured the same quantity.
- Never compute MLD from monthly means and call it the monthly MLD
  without the shallow-bias caveat.
- Never use a temperature criterion where barrier layers are plausible
  without checking against a density criterion.
- Never present an MLD conclusion without a threshold-sensitivity
  check.
