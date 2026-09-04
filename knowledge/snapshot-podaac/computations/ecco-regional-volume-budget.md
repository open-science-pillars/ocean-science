---
type: Attested Computation
title: "Regional volume budget over a control volume from ECCO v4r4 (attested)"
description: "The volume variant of the regional budget contract, whose sabotage set makes the documented freshwater double-count a mandatory catch: every receipt proves that ADDING a separate surface forcing term breaks the closure."
tags: [ecco, volume-budget, regional, control-volume, attested, native-grid]
runtime: python
parameters:
  - { name: budget, type: "volume", required: true }
  - { name: region or box with depth-m, type: "as the heat variant", required: true }
  - { name: year, type: "int, default 2010", required: false }
computation: references/computations/ecco_regional_budget.py
executor:
  resource: references/computations/ecco_regional_budget.py
  receipt: [run_id, code_sha256, data, bound_parameters, resolved_volume, results, mutation_evidence, caveats]
attester:
  resource: references/attesters/regional_budget_check.py
generated: { by: claude-code/fable-5, at: 2026-09-01T15:40:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-04T02:58:02Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: regional-heat
    resource: ecco-regional-heat-budget.md
    title: "The heat variant that defines the shared contract"
  - id: pointwise-volume
    resource: ../recipes/ecco-volume-budget.md
    title: "The signed pointwise volume budget: closure on transport convergence alone, the 1e-11 per s tolerance, and the freshwater double-count this variant turns into a mandatory demonstration"
---

# Regional volume budget over a control volume from ECCO v4r4 (attested)

The volume budget closed over a control volume: tendency d(s*)/dt,
rim as UVELMASS times dyG times drF and VVELMASS times dxG times drF
(no partial-cell factor, the MASS suffix carries it), vertical faces
as WVELMASS times rA INCLUDING the surface face, which carries the
freshwater flux, so the budget takes NO separate forcing
term.[^pointwise-volume] Bars: absolute 1e-11 per s per unit volume,
relative 1e-6.[^regional-heat]

The sabotage set turns the bundle's documented double-count into
evidence every receipt must carry: spurious-freshwater-forcing-added
reruns the budget WITH a separate surface freshwater forcing term and
must be caught, always structural, never applicability-aware. A
receipt for this budget is therefore also a demonstration that the
double-count breaks closure in the chosen volume.

**Reference run (2026-09-01, southeast-atlantic-upper, year 2010).**
Residual per volume max 1.068e-15 per s against the 1e-11 bar;
relative 5.489e-07; all four sabotages caught, the spurious
freshwater term among them. Attester PASS; FAIL demonstrated on the
double-count sabotage removed from the evidence.

**Data provenance.** The receipt also carries a `data` block: the data
root and the `RECORD.json` stamp the verify tool leaves in a tree it has
checked against its manifest (record name, manifest SHA-256,
verification time, report SHA-256). The attester refuses a receipt
whose `data.record` is not that stamp, so nothing is attested against a
tree this bundle has not manifested and verified. The two trees and
the rule are in docs/science-record.md.

[^regional-heat]: computations/ecco-regional-heat-budget.md, the shared contract
[^pointwise-volume]: recipes/ecco-volume-budget.md, closure on convergence alone
