---
type: Attested Computation
title: "Regional salt budget over a control volume from ECCO v4r4 (attested)"
description: "The salt variant of the regional budget contract: SLT fluxes at the rim, the three-dimensional salt plume tendency with the surface salt flux at the top level only, and applicability-aware sabotages that record honestly when a term cannot matter in the chosen volume."
tags: [ecco, salt-budget, regional, control-volume, attested, native-grid]
runtime: python
parameters:
  - { name: budget, type: "salt", required: true }
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
    title: "The heat variant that defines the shared contract: two bars, mutation evidence, mask disclosure, single-tile v1 limit"
  - id: pointwise-salt
    resource: ../recipes/ecco-salt-budget.md
    title: "The signed pointwise salt budget whose formulation and absolute tolerance (1.5e-10 g per kg per s) this inherits"
---

# Regional salt budget over a control volume from ECCO v4r4 (attested)

The salt budget closed over a control volume: tendency d(s* SALT)/dt
from snapshots, the SLT advective and diffusive fluxes read raw at the
rim and the vertical faces, and forcing as the THREE-DIMENSIONAL salt
plume tendency with the surface salt flux added at the top level only,
no shortwave, no geothermal.[^pointwise-salt] Contract, disclosure,
and the explicit-box tier are the heat variant's, with the salt bars:
absolute 1.5e-10 g per kg per s per unit volume, relative
1e-6.[^regional-heat]

Five sabotages per receipt: the three structural ones (rim shifted,
vertical sign flipped, vertical faces omitted) plus two
applicability-aware term omissions, the surface salt flux and the
salt plume. In the reference volume both record applicable false with
their measured numbers: the southeast Atlantic upper ocean receives
too little of either for omission to cross a bar, which is physics
disclosed, not a test weakened. A high-latitude volume would flip
both to mandatory catches.

**Reference run (2026-09-01, southeast-atlantic-upper, year 2010).**
Residual per volume max 3.056e-14 g per kg per s against the 1.5e-10
bar; relative 5.594e-07. Attester PASS; FAIL demonstrated on a caught
flag contradicting its own numbers.

**Data provenance.** The receipt also carries a `data` block: the data
root and the `RECORD.json` stamp the verify tool leaves in a tree it has
checked against its manifest (record name, manifest SHA-256,
verification time, report SHA-256). The attester refuses a receipt
whose `data.record` is not that stamp, so nothing is attested against a
tree this bundle has not manifested and verified. The two trees and
the rule are in docs/science-record.md.

[^regional-heat]: computations/ecco-regional-heat-budget.md, the shared contract
[^pointwise-salt]: recipes/ecco-salt-budget.md, the inherited formulation
