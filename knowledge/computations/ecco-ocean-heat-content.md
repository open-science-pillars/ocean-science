---
type: Attested Computation
spheres: [hydrosphere]
title: "Global ocean heat content from ECCO v4r4 (attested)"
description: "Sanctioned volume-weighted OHC computation with grid anchors; a run passes attestation only with the sanctioned code, the contract parameters, tutorial-anchored geometry, and the potential-temperature baseline caveat in the receipt."
tags: [ecco, ocean-heat-content, ohc, attested, native-grid]
runtime: python
parameters:
  - { name: months, type: "list of YYYY-MM strings", required: true }
computation: skills/ecco/scripts/ecco_ohc.py
executor:
  resource: skills/ecco/scripts/ecco_ohc.py
  receipt: [run_id, code_sha256, data, bound_parameters, anchors, months, ohc_J_by_month, ohc_change_J, cells_evaluated, ohc_baseline_caveat]
attester:
  resource: skills/ecco/scripts/ohc_check.py
generated: { by: claude-code/fable-5, at: 2026-09-01T05:11:19Z }
verified:
  - { by: human:PaulMRamirez, at: 2026-09-05T16:14:15Z }
  - { by: human:PaulMRamirez, at: 2026-09-16T05:51:09Z, role: maintainer, source: https://github.com/open-science-pillars/nasa-daac-knowledge/pull/183 }
status: draft
stale_after: 2027-01-04
sources:
  - id: budget-formulation
    resource: knowledge/podaac/conventions/ecco-budget-formulation.md
    title: "Bundle convention, ECCO v4r4 budget formulation: the MITgcm constants rhoConst 1029 and Cp 3994"
  - id: tutorial-scalar
    resource: https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Example_calculations_with_scalar_quantities.html
    title: "ECCO v4 Python tutorial, scalar quantities: publishes total ocean surface area 3.58E+08 km2, the grid anchor"
  - id: ecco-skills-corroboration
    resource: https://github.com/podaac/ecco-skills
    title: "podaac/ecco-skills compute-ocean-heat-content acceptance record: independently measured the same anchors (area exact to the tutorial, volume within 0.4 percent of literature, volume-mean THETA 3.594 degC)"
  - id: trend-ci
    resource: ecco-trend-ci.md
    title: "Attested computation, trend with interval: reads a monthly mapping out of a sanctioned receipt and copies its data stamp forward"
---

# Global ocean heat content from ECCO v4r4 (attested)

**Placement, 2026-09-20 (ADR E, a computation is a skill).** This
concept came from the nasa-daac-knowledge bundle at
`knowledge/podaac/computations/ecco-ocean-heat-content.md`, and the
executor and the attester it names now ship in this package under
`skills/ecco/scripts/`. The golden `verification/ecco_dynamics.py` names
every script it does. The executor `skills/ecco/scripts/ecco_ohc.py` is
byte for byte the file that was under the bundle, so its sha256
e28b085edb5e708e and every receipt that names it stand. The reference
run `ohc` reads the ECCO 2010 fixture cache, which this environment does
not hold, so it was not re-run here; the golden runs it where the cache
is present. The signature block is the one the maintainer left; the
concept sits at `status: draft` with no verified event added, and the
maintainer re-signs it after merge.

OHC as the volume-weighted sum of potential temperature over wet
cells, rhoConst times Cp times the sum of THETA times rA times drF
times hFacC, with the MITgcm constants the budget formulation
convention records (rhoConst 1029 kg m-3, Cp 3994 J kg-1 K-1).[^budget-formulation]
THETA is potential temperature, so an absolute OHC is relative to an
arbitrary 0 degC baseline; the receipt carries that caveat as a
required field and the attester fails any receipt that drops it.

**Attestation contract.** A run passes only when the receipt's
code_sha256 matches the sanctioned computation file, the bound
parameters are exactly the contract set (months, the fixed collection,
the two constants), the grid anchors hold (ocean surface area within
0.5 percent of the tutorial-published 3.58E+08 km2, measured deviation
0.003 percent; ocean volume within 1 percent of the literature
1.335E+18 m3, measured deviation under 0.01 percent; exactly 2,406,992
wet cells), every month's volume-mean THETA sits in the
provisional 2 to 6 degC physical band, and the monthly series
`ohc_J_by_month` covers the bound months in order and agrees with the
per-month list to the last bit.[^tutorial-scalar]

**The monthly series is a receipt field, not a by-product.** The
receipt carries the monthly OHC as `ohc_J_by_month`, a `{YYYY-MM: J}`
mapping, because that is the form the trend-with-interval computation
reads (`ecco_trend_ci.py --source ohc_receipt.json --field
ohc_J_by_month --value-units J --scale 1e-21 --report-units ZJ`). A
deseasonalized OHC series or an OHC trend fitted that way inherits
this receipt's run id, code hash and data stamp, and its attester
recomputes the chain from the series in the trend receipt; a series
retyped into a bare file attests FAIL by construction, whatever its
arithmetic.[^trend-ci] The deseasonalized monthly series a plot wants
is the trend receipt's `intermediates.series_fit`.

**Reference chain on the science record (2026-09-05).** All 312
months 1992-01 to 2017-12 in one run: OHC change +1.8099E+23 J,
attester PASS. The trend over that series with the seasonal cycle
removed: +8.06 ZJ/yr, 95 percent interval [+3.48, +12.63], lag-1
autocorrelation 0.978 leaving 3.5 effective samples of 312, trend
attester PASS with the OHC receipt's stamp copied forward. The wide
interval is the honest one: a 26-year OHC series carries decadal
persistence, and the naive interval (half width 0.10 ZJ/yr) would
overstate the certainty forty-fold.

**Reference run (2026-09-01, cached native granules).** Surface area
3.5801E+08 km2; volume 1.3350E+18 m3; volume-mean THETA 3.6085 degC
(2010-01) and 3.6068 degC (2010-12); OHC change 2010-01 to 2010-12 of
-9.485E+21 J. Attester PASS on the run; FAIL demonstrated on a
one-character code tamper (sha mismatch) and on a doctored volume
anchor. The same anchors were measured independently by the PO.DAAC
ecco-skills project, which reached them with different code and no
contact with this bundle: area exact to the tutorial, volume within
0.4 percent, volume-mean THETA 3.594 degC for its
month.[^ecco-skills-corroboration]

**Data provenance.** The receipt also carries a `data` block: the data
root and the `RECORD.json` stamp the verify tool leaves in a tree it has
checked against its manifest (record name, manifest SHA-256,
verification time, report SHA-256). The attester refuses a receipt
whose `data.record` is not that stamp, so nothing is attested against a
tree this bundle has not manifested and verified. The two trees and
the rule are in docs/science-record.md.

[^budget-formulation]: Bundle convention, ECCO v4r4 budget formulation, constants section
[^tutorial-scalar]: ECCO v4 tutorial scalar-quantities chapter, the published ocean surface area
[^ecco-skills-corroboration]: podaac/ecco-skills OHC acceptance record, an independent implementation reaching the same anchors
[^trend-ci]: computations/ecco-trend-ci.md, the one sanctioned trend method and its chain-of-custody rule
