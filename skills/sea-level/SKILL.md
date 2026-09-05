---
name: sea-level
description: "Sea level components: steric, manometric, GRACE ocean bottom pressure, altimetry SSH, budget closure caveats."
user-invocable: false
---

# sea-level

Background expertise for sea level work where the corrections are the
analysis.

## Consult the bundle first

Before any sea level statement, consult installed knowledge concepts
first, as the core `consult-knowledge` skill sets out (the directories
to glob, how to voice a concept's status, which concept wins on
conflict), by product name (GRACE, ECCO, altimetry), by correction
(GIA, inverse barometer, leakage), and by topic (steric, manometric,
budget closure, trend); read the matches, and restate what each changes
about the plan before computing, citing it by path. The concepts this
plugin resolves to today: the ECCO concepts the ecco skill lists (the
SSH and OBP family concepts, the SSH inverse-barometer and release
gotchas, the Boussinesq global-steric gotcha, the trend gotchas, the
regional sea-level and steric computations, the sea-level findings and
validity domains); the GRACE dataset concept and its leakage and GIA
gotchas; the altimetry concepts (the NASA-SSH dataset and the
SSH-versus-altimetry computation); and the plugin's own connector
concepts under `knowledge/connectors/` for tide gauges and Argo. The
sea level budget bookkeeping lives in
`knowledge/podaac/conventions/sea-level-budget-closure.md`; the GRACE effective
resolution, coastal-leakage, and GIA facts live in the GRACE dataset
concept and its gotchas; the ECCO SSH-variant, V4R4/V4R4B release, and
Boussinesq facts live in the ECCO concepts. A concept added or corrected
since you last ran is found this way, and that is how a new or corrected
concept changes this skill's behavior without editing this file. Never
carry those numbers or rules here.

## The decomposition (method)

Sea surface height change splits into steric (density change:
thermosteric plus halosteric, no mass change) and manometric (mass
change, what ocean bottom pressure sees). Globally: barystatic (land-ice
and land-water mass input) plus global-mean thermosteric. Regionally,
redistribution dominates both, and decadal dynamic variability commonly
swamps the local trend. Every sea level statement names which component
it concerns.

## The three observing systems and their frames (method)

Each observing system measures a different component in a different frame;
the product-specific corrections, resolutions, and depth limits are read
from the concepts, not restated here.

- **Altimetry (SSH):** geocentric sea surface height; the corrections
  (inverse barometer, tides, GIA for trends) define the product, so the
  applicable altimetry concept is consulted for which are applied.
- **Gravimetry (GRACE/GRACE-FO mascons):** ocean mass, i.e., the
  manometric piece. Its effective resolution, coastal leakage, and the
  baked-in GIA correction are first-order and live in the GRACE dataset
  concept and its gotchas; consult and cite them.
- **Hydrography (Argo-era T/S):** steric height, over the sampled depth
  range only. The deep-steric term below the Argo sampling floor is not
  measured by it and is not zero; the budget-closure convention carries
  that caveat.

## Budget closure

The sea level budget (altimetry = ocean mass + steric) closes within
uncertainties only when the bookkeeping is consistent across products:
GIA, reference frame, atmospheric-pressure (inverse-barometer)
convention, effective smoothing (gravimetry's footprint against pointwise
altimetry), period, and the deep-steric term. Those consistency
requirements live in
`knowledge/podaac/conventions/sea-level-budget-closure.md`; consult and restate
them for the products in play. Apparent non-closure is a
correction-consistency finding before it is a missing-physics finding:
work the corrections table first (that ordering is the hard refusal
below).

## Trends (method)

Trend work inherits every caveat above plus time-sampling: altimetry
trends need GIA and are era-dependent; GRACE trends can depend on the
GIA-model choice more than on measurement noise for some basins (the
GRACE GIA gotcha owns that sensitivity, consult it); regional trends must
be tested against internal variability (basic-statistics'
autocorrelation-aware methods); and the global-mean anchor lives in
analysis-review's smell-test table, not here.

## Hard refusals

- **Never declare sea level budget non-closure before auditing correction
  consistency.** (Invariant, gate-shaped, universal: an apparent
  altimetry-minus-mass-minus-steric mismatch is a correction-bookkeeping
  finding first, whatever the products; work the corrections table before
  concluding missing physics.)

Everything else that used to sit here as a "must not" restated a dataset
gotcha and now lives in its concept, consulted per the step above: mixing
inverse-barometer conventions or ECCO V4R4 and V4R4B releases, comparing
altimetry, GRACE, and steric under inconsistent GIA, treating Argo-era
steric as full-depth, and quoting a Boussinesq global-mean sea level
without the mass-conservation correction. Read them from the concepts; do
not re-inline the numbers or the rules here.
