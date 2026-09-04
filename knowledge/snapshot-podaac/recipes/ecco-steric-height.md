---
type: recipe
title: "Steric height and its trend from ECCO v4r4 density"
description: "Column-integrated steric height from RHOAnoma on the native grid: the hFac weighting, the region registry, and the Boussinesq limit that makes a global mean a diagnostic, not a sea level."
tags: [ecco, steric-height, sea-level, recipe, native-grid]
inputs: "ECCO_L4_DENS_STRAT_PRESS_LLC0090GRID_MONTHLY_V4R4 (RHOAnoma) for the chosen months; the geometry granule (rA, drF, hFacC, maskC)"
expected: "Reference region us-northeast-coast, 2010-01 through 2010-12 (measured 2026-09-01): steric trend +135.7772 mm per year over 102 wet columns, matching the attested sea-level partition's signed receipt to four decimals, with a 95 percent interval of [-701.5, +973.1] (measured 2026-09-02), so the year cannot tell its trend from zero; over the full record 1992-01 through 2017-12 the trend is +2.7999 mm per year with interval [+1.5103, +4.0895], from both computations; regional area-mean steric height near -19.6 m"
expected_uncertainty: "Any area-mean outside -60 to 0 m is suspect. A GLOBAL mean steric height is a Boussinesq diagnostic: the model conserves volume, not mass, so global steric change does not translate to modeled sea-surface rise and the attested form refuses to report it without that caveat"
generated: { by: claude-code/fable-5, at: 2026-09-01T05:35:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-02T14:51:04Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: attested-computation
    resource: ../computations/ecco-steric-height.md
    title: "The attested computation this recipe walks: contract, cross-computation anchor, reference run"
  - id: sea-level-partition
    resource: ../computations/ecco-regional-sea-level.md
    title: "The attested sea-level partition whose steric term anchors the reference trend"
  - id: trend-ci
    resource: ../computations/ecco-trend-ci.md
    title: "The sanctioned trend method that states the interval beside every trend here"
---

# Steric height and its trend from ECCO v4r4 density

Steric height is the sea-level contribution of density change: for
each column, minus one over rho0 times the vertical sum of RHOAnoma
times hFacC times drF, with hFacC doing the same partial-cell and
land-mask work it does in every native-grid integral. Area-weight by
rA over the region, fit the sanctioned trend (a least-squares slope,
jointly with the monthly climatology over complete years), and report
mm per year with the 95 percent interval that method states beside
it, never the trend alone.[^attested-computation][^trend-ci]

The number to reproduce: over the US northeast coast box for 2010 the
trend is +135.7772 mm per year, and the attested sea-level partition,
computed from different code, records the same value in its signed
receipt to four decimals.[^sea-level-partition] That agreement is the
recipe's anchor: two independent routes to the same physical quantity
through the same bundle. Beside the anchor sits its interval, [-701.5,
+973.1] mm per year: twelve months of a series with lag-1
autocorrelation +0.555 hold 3.43 effective samples, so the number is a
description of 2010, not a rate. Over the full record, 1992-01
through 2017-12, the two routes agree again at +2.7999 mm per year
with interval [+1.5103, +4.0895], and that one is a
rate.[^trend-ci] The limit to respect: globally, ECCO is
Boussinesq (volume-conserving), so a global-mean steric change is a
water-mass diagnostic, not a modeled sea-surface rise; the attested
form carries that caveat as a required receipt field.[^attested-computation]

[^attested-computation]: computations/ecco-steric-height.md, contract and reference run
[^sea-level-partition]: computations/ecco-regional-sea-level.md, the signed steric trend
[^trend-ci]: computations/ecco-trend-ci.md, the method behind every interval here
