---
type: Attested Computation
title: "Global ocean heat content from ECCO v4r4 (attested)"
description: "Sanctioned volume-weighted OHC computation with grid anchors; a run passes attestation only with the sanctioned code, the contract parameters, tutorial-anchored geometry, and the potential-temperature baseline caveat in the receipt."
tags: [ecco, ocean-heat-content, ohc, attested, native-grid]
runtime: python
parameters:
  - { name: months, type: "list of YYYY-MM strings", required: true }
computation: references/computations/ecco_ohc.py
executor:
  resource: references/computations/ecco_ohc.py
  receipt: [run_id, code_sha256, data, bound_parameters, anchors, months, ohc_change_J, cells_evaluated, ohc_baseline_caveat]
attester:
  resource: references/attesters/ohc_check.py
generated: { by: claude-code/fable-5, at: 2026-09-01T05:11:19Z }
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: budget-formulation
    resource: ../conventions/ecco-budget-formulation.md
    title: "Bundle convention, ECCO v4r4 budget formulation: the MITgcm constants rhoConst 1029 and Cp 3994"
  - id: tutorial-scalar
    resource: https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Example_calculations_with_scalar_quantities.html
    title: "ECCO v4 Python tutorial, scalar quantities: publishes total ocean surface area 3.58E+08 km2, the grid anchor"
  - id: ecco-skills-corroboration
    resource: https://github.com/podaac/ecco-skills
    title: "podaac/ecco-skills compute-ocean-heat-content acceptance record: independently measured the same anchors (area exact to the tutorial, volume within 0.4 percent of literature, volume-mean THETA 3.594 degC)"
---

# Global ocean heat content from ECCO v4r4 (attested)

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
wet cells), and every month's volume-mean THETA sits in the
provisional 2 to 6 degC physical band.[^tutorial-scalar]

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
