---
type: Attested Computation
title: "Regional heat budget over a control volume from ECCO v4r4 (attested)"
description: "Closed heat budget over a registered region or an explicit box, validated across three independent collections; two bars, mutation evidence in every receipt, and the resolved mask disclosed by digest because no oracle can check it is the water the user meant. The sanctioned executor also serves the salt and volume budgets under their own contracts."
tags: [ecco, heat-budget, regional, control-volume, attested, native-grid]
runtime: python
parameters:
  - { name: region, type: "registered region name", required: false }
  - { name: box, type: "LAT0 LAT1 LON0 LON1 with depth-m; explicit tier", required: false }
  - { name: year, type: "int, default 2010", required: false }
computation: references/computations/ecco_regional_budget.py
executor:
  resource: references/computations/ecco_regional_budget.py
  receipt: [run_id, code_sha256, data, bound_parameters, resolved_volume, results, mutation_evidence, caveats]
attester:
  resource: references/attesters/regional_budget_check.py
generated: { by: claude-code/fable-5, at: 2026-09-01T15:00:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-04T02:40:20Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: design-note
    resource: ../../../docs/regional-budget-design.md
    title: "The regional budget design note: the two-bar finding, the tautology retraction, the disclosure doctrine, and the measured demonstration this computation promotes"
  - id: pointwise-budget
    resource: ecco-heat-budget.md
    title: "The attested pointwise heat budget whose formulation, constants, and absolute tolerance this computation inherits"
  - id: geothermal-gotcha
    resource: ../gotchas/ecco-geothermal-flux.md
    title: "The geothermal gotcha: the term a PO.DAAC-only budget omits silently, and the measured proof the absolute bar alone cannot catch that omission"
---

# Regional heat budget over a control volume from ECCO v4r4 (attested)

A heat budget closed over a control volume by comparing THREE
independent collections, so agreement is evidence rather than
arithmetic: tendency from temperature and sea-surface-height
snapshots, transport from the three-dimensional flux collection read
as raw face fluxes at the volume's boundary (never derived from the
divergence field; the telescoping identity holds for random noise and
proves nothing), and forcing from the surface flux collection plus
geothermal at bottom wet cells.[^design-note] Formulation, constants,
shortwave penetration, and free-surface scaling are inherited from the
attested pointwise budget.[^pointwise-budget]

**Attestation contract.** TWO BARS, both required: the absolute
per-volume residual within 1e-10 degC per s (the signed pointwise
tolerance) AND the residual relative to the largest regional term
within 1e-6. The receipt states the units of its residual and bar
(degC per s here; g per kg per s and per s for the salt and volume
variants) and the attester refuses a receipt whose stated units are
not the budget's own. Measured 2026-08-31: omitting geothermal flux lands at
1.24e-12, inside the absolute bar, and is caught only by the relative
bar, so one bar is not a criterion.[^geothermal-gotcha] Every receipt
carries MUTATION EVIDENCE: the executor reruns four sabotages
(geothermal omitted, rim face shifted one cell, vertical face sign
flipped, vertical faces omitted) and records each failing a bar; a
structural sabotage that cannot fail aborts the run with no receipt.
The geothermal sabotage alone is applicability-aware: a volume with
few or no bottom cells owes no geothermal catch, and the entry then
records applicable false with its measured numbers and the disclosed
bottom-cell count, a story the attester checks for internal
consistency. The resolved volume travels fully disclosed: index
bounds, tile, depth face, latitude and longitude extent, wet and
bottom cell counts, volume, a digest of the resolved wet mask, and
the geometry granule digest, because no oracle can check that a mask
is the water the user meant; disclosure is the answer.[^design-note]
Stated v1 limit: the volume must lie within one tile interior;
seam-crossing volumes are refused until the seam-calibrated section
machinery lands.

**Reference run (2026-09-01, cached native granules, year 2010,
region southeast-atlantic-upper: tile 1 index box, roughly 44S to 10S
and 18W to 22E, upper 323 m, 27,921 wet cells, 4.1351e15 m3).**
Residual per volume max 1.352e-14 degC per s; relative max 1.533e-07 (remeasured 2026-09-01 after the executor generalized to salt and volume with float64 rim accumulation);
all four mutations caught. Attester PASS on the run; FAIL demonstrated
on a doctored FLATTERING residual (1e-16 trips the two-sided
reference anchor), on dropped mutation evidence, on a dropped mask
digest, and on a receipt whose geothermal caught flag contradicts its
own numbers. Explicit-box tier demonstrated: a requested box of 40S
to 20S, 10W to 10E at 300 m resolved to 9,600 wet cells and 1.4219e15
m3, closed at 2.041e-14 with geothermal recorded not applicable, and
passed attestation on the general contract.

**Data provenance.** The receipt also carries a `data` block: the data
root and the `RECORD.json` stamp the verify tool leaves in a tree it has
checked against its manifest (record name, manifest SHA-256,
verification time, report SHA-256). The attester refuses a receipt
whose `data.record` is not that stamp, so nothing is attested against a
tree this bundle has not manifested and verified. The two trees and
the rule are in docs/science-record.md.

[^design-note]: docs/regional-budget-design.md, the oracle, the retraction, and the disclosure doctrine
[^pointwise-budget]: computations/ecco-heat-budget.md, the inherited formulation and tolerance
[^geothermal-gotcha]: gotchas/ecco-geothermal-flux.md, and the measured 1.24e-12 omission inside the absolute bar
