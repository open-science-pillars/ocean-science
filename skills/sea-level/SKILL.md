---
name: sea-level
description: "Sea level components: steric, manometric, GRACE ocean bottom pressure, altimetry SSH, budget closure caveats."
user-invocable: false
---

# sea-level

Background expertise for sea level work where the corrections are the
analysis.

## The decomposition

Sea surface height change splits into steric (density change:
thermosteric plus halosteric, no mass change) and manometric (mass
change, what ocean bottom pressure sees). Globally: barystatic
(land-ice and land-water mass input) plus global-mean thermosteric.
Regionally, redistribution dominates both, and decadal dynamic
variability commonly swamps the local trend. Every sea level statement
names which component it concerns.

## The three observing systems and their frames

- **Altimetry (SSH):** geocentric sea surface height; corrections
  define the product (inverse barometer, tides, GIA for trends).
- **Gravimetry (GRACE/GRACE-FO mascons):** ocean mass, i.e., the
  manometric piece; coarse effective resolution (order 300 km),
  coastal leakage, and the GIA correction choice are first-order; the
  bundle's GRACE-FO dataset concept and gotchas  carry
  the details.
- **Hydrography (Argo-era T/S):** steric height, sampled to about
  2000 m; the deep steric contribution below Argo is not measured by
  it and is not zero.

## Budget closure caveats

The sea level budget (altimetry = GRACE mass + steric) closes within
uncertainties ONLY when the bookkeeping is consistent: the same GIA
model applied compatibly to altimetry and gravimetry, compatible
reference frames and atmospheric-pressure conventions, comparable
effective smoothing (GRACE's footprint against pointwise altimetry),
matching periods, and the deep-steric term acknowledged. Apparent
non-closure is a correction-consistency finding before it is a
missing-physics finding; work the corrections table first.

## ECCO specifics

- The SSH family (variable catalog row) is convention-laden: SSH
  (IB-corrected, GIA-free model sea level), SSHNOIBC, SSHIBC, and the
  model native ETAN; comparisons against altimetry pick the variant
  matching the altimetry product's IB convention, and say so.
- **Release discipline: SSH and OBP are exactly the two ECCO product
  families with corrected V4R4B releases** (catalog Variants section);
  a sea level analysis mixing V4R4 and V4R4B granules, or comparing
  against literature pinned to the other release, shifts results
  silently. State the release in the methods.
- Boussinesq models conserve volume, not mass: ECCO's global-mean
  steric sea level needs the standard global correction (Greatbatch
  adjustment) before global budgets; regional patterns are unaffected.

## Trends

Trend work inherits every caveat above plus time-sampling: altimetry
trends need GIA and are era-dependent; GRACE trends depend on the GIA
model choice more than on measurement noise for some basins; regional
trends must be tested against internal variability (basic-statistics'
autocorrelation-aware methods), and the global-mean anchor lives in
analysis-review's smell-test table, not here.

## Must NOT

- Never mix IB conventions, or V4R4 and V4R4B releases, within one
  analysis or comparison without stating it.
- Never compare altimetry, GRACE, and steric estimates under
  inconsistent GIA treatments.
- Never declare sea level budget non-closure before auditing
  correction consistency.
- Never treat Argo-era steric as full-depth steric.
- Never quote a Boussinesq model's global-mean sea level without the
  mass-conservation correction.
