---
name: mixed-layer
description: "Mixed layer depth: density and temperature criteria, seasonal cycle, sensitivity to threshold choice."
user-invocable: false
---

# mixed-layer

Background expertise for mixed layer depth (MLD) work, where the answer
depends on the definition. This skill carries the METHOD (what an MLD
is, what makes two MLDs comparable, the sensitivity discipline) and the
hard refusals. The criterion thresholds, the named schemes, the
averaging and comparability numbers, the barrier-layer regimes, and any
product's built-in MLD diagnostic live in the knowledge bundle and are
read from there per analysis, never restated here.

## Consult the bundle for this analysis

Before any MLD work, DISCOVER and read the applicable concepts; do not
work from a remembered list of thresholds or caveats. Glob and grep
`knowledge/conventions/`, `knowledge/gotchas/`, and `knowledge/datasets/`
for every concept touching MLD criteria, the products in play, and the
regime (search "mixed layer", "mld", a criterion name, a product name).
Read the matches, restate what each changes about the plan, and cite it
by path before computing. The criterion families and their threshold
values, the comparability and input-averaging rules, the monthly-mean
shallow bias, the barrier-layer regimes, and a product's own MLD
diagnostic are read from the bundle (for example
`knowledge/conventions/mld-criteria.md` and the MLD gotchas such as
`knowledge/gotchas/ecco-mxldepth-criterion.md`), never from this file. A
concept added or corrected since you last ran is found this way.

## MLD is a criterion, not an observable (method)

Every MLD number embeds a definition: a criterion family (density,
temperature, gradient, or hybrid), a reference depth, and a threshold.
Change any one and the number changes, most dramatically in weak
stratification and in winter deep-mixing regions. The standard
thresholds, the named schemes, and the magnitudes of these differences
are convention facts and are read from the bundle, not carried here.

## Comparability (method)

MLD values are the same physical quantity only under the SAME criterion,
reference depth, threshold, AND input averaging. When comparing
products, recompute under one criterion rather than mixing definitions;
state the criterion, reference depth, threshold, and averaging chain
with every MLD number. Which values must match, and the size of the
biases that mixing them introduces (the monthly-mean shallow bias, the
barrier-layer overestimate, a product's own-criterion diagnostic), are
read from the bundle's concepts.

## Seasonal cycle and regimes (physics)

The seasonal cycle spans roughly an order of magnitude: shallow summer
mixed layers, deep winter ones, deepest in the winter deep-convection
regions. The winter maximum sets ventilation and mode-water formation
(see water-masses); the summer minimum sets the biologically active
layer. Deep convection is episodic, so a climatological winter MLD (a
climatological March in the Labrador Sea, say) is an average over
convecting and non-convecting years, not a typical winter, and is
stated as such.

## Sensitivity discipline (method)

Any MLD-derived conclusion carries a sensitivity check: recompute under
at least one alternative threshold (or criterion family) and report
whether the conclusion survives. Threshold sensitivity IS the
uncertainty statement for MLD (uncertainty-quantification's house rule
applies; there is no instrument error bar to quote for a definition).

## Must NOT (hard refusals and gates)

- Never report an MLD without its criterion, threshold, reference depth,
  and input averaging. (Hard refusal: invariant, universal.)
- Never compare MLDs across products computed with different criteria as
  if they measured the same quantity; recompute under one criterion.
  (Hard refusal.)
- Never present an MLD conclusion without a threshold-sensitivity check.
  (Hard refusal.)
- Never present MLD computed from monthly-mean profiles as the monthly
  MLD without the averaging-bias caveat; consult the bundle for the
  mechanism and its magnitude, do not restate it here. (Gate.)
- Never use a temperature criterion where barrier layers are plausible
  without cross-checking against a density criterion; consult the bundle
  for which regimes this affects. (Gate.)

Dataset- and convention-specific facts (the threshold values, the named
schemes, the comparability and averaging numbers, the monthly-mean
shallow bias, the barrier-layer regimes, and any product's own MLD
diagnostic) are NOT restated here: they live in the bundle's concepts
and are consulted per the step above. That is what lets a corrected
threshold or a new MLD gotcha change this skill's behavior without
editing it.
