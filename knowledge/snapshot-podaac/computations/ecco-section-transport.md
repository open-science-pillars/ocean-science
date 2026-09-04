---
type: Attested Computation
title: "Section transports on the ECCO v4r4 native grid (attested)"
description: "Volume and heat transport across registered sections by signed indicator-gradient face masks over a budget-verified tile topology; anchored against an independent implementation, with five sabotages recorded in every receipt and unanchored sections required to say so."
tags: [ecco, transport, section, seam, attested, native-grid]
runtime: python
parameters:
  - { name: section, type: "registered section name", required: true }
  - { name: year, type: "int, default 2010", required: false }
computation: references/computations/ecco_section_transport.py
executor:
  resource: references/computations/ecco_section_transport.py
  receipt: [run_id, code_sha256, data, bound_parameters, resolved_section, results, mutation_evidence, caveats]
attester:
  resource: references/attesters/section_transport_check.py
generated: { by: claude-code/fable-5, at: 2026-09-01T15:20:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: transport-golden
    resource: https://github.com/open-science-pillars/ocean-science/blob/14a4eeab071d6f7d10f04e72c4878fef87c8b8de/verification/transport_analysis.py
    title: "The independent implementation this computation is anchored against: meridional heat transport via ecco_v4_py, 2010 global mean 1.098 PW at 26.5 north"
  - id: mht-26n-recipe
    resource: ../recipes/ecco-mht-26n.md
    title: "The recipe that records the 1.098 PW global-circle anchor and its 2010 monthly series"
  - id: regional-budget
    resource: ecco-regional-heat-budget.md
    title: "The attested regional budget whose two-bar and mutation-evidence contract this computation extends to sections"
  - id: vector-orientation
    resource: ../gotchas/ecco-vector-orientation.md
    title: "The vector-orientation gotcha the rotated-tile sabotage exercises: native components are tile-local"
---

# Section transports on the ECCO v4r4 native grid (attested)

Transport across a section built the indicator-gradient way: an
indicator marks the region on one side, and every stored face whose
two adjacent cells disagree is a section face, signed so positive
transport crosses into the region. Faces are enumerated as STORED
(each physical face exists once in the archive), and a face on a tile
edge takes its outside cell from the neighbor per a topology table
lifted from ecco_v4_py 1.8.1 and then verified twice on 2026-09-01:
geometrically (all 24 connected edges map neighbor cells within one
local spacing; same-axis joins parallel, cross-axis joins reversed, no
sign flip) and BY PHYSICS: the pointwise heat budget evaluated on all
683,496 seam-adjacent cell months of 2010 with these mappings closes
at max 2.1e-11 degC per s, inside the interior tolerance, median
5.4e-14 equal to the interior's. A wrong mapping cannot close at
round-off; the budget is the oracle, and no separate seam tolerance
proved necessary.[^regional-budget]

Weighting is per collection and opposite by design: the heat fluxes
are already face-integrated and take NO weighting; the mass-weighted
velocities take face length times layer thickness and NO partial-cell
factor. Every receipt records five sabotages with their measured
transport deltas: rotated-tile face signs flipped, south-face
component dropped, path shifted one row, seam-owned faces dropped,
and ghost tables zeroed, the error a section tool that ignores tile
topology commits silently.[^vector-orientation] Structural sabotages
that cannot fail abort the run receiptless; the rest record applicable
false with their numbers, and the attester checks every flag against
the numbers it travels with.

**Reference runs (2026-09-01, cached native granules, year 2010).**
global-26.5n, the closed latitude circle, 360 faces: heat transport
mean +1.0963 PW against the independent implementation's 1.098, an
0.002 PW cross-implementation agreement from disjoint code
paths;[^transport-golden][^mht-26n-recipe] volume mean -0.43 Sv, the real net
throughflow scale. fifteen-s-southeast-atlantic, an open 90-face
segment within one tile: heat -0.28 PW, volume -10.56 Sv, and its
receipt must carry the unanchored caveat; the attester fails a
benchmark-free transport that does not declare itself. Demos: PASS on
both sections; FAIL on a heat mean doctored toward the anchor (the
two-sided measured band catches what the anchor band alone would
admit); FAIL on the dropped unanchored caveat; FAIL on a sabotage
removed from the evidence.

**Data provenance.** The receipt also carries a `data` block: the data
root and the `RECORD.json` stamp the verify tool leaves in a tree it has
checked against its manifest (record name, manifest SHA-256,
verification time, report SHA-256). The attester refuses a receipt
whose `data.record` is not that stamp, so nothing is attested against a
tree this bundle has not manifested and verified. The two trees and
the rule are in docs/science-record.md.

[^transport-golden]: ocean-science verification/transport_analysis.py at the pinned commit, the independent implementation
[^mht-26n-recipe]: recipes/ecco-mht-26n.md, the recorded 1.098 PW global-circle anchor
[^regional-budget]: computations/ecco-regional-heat-budget.md, the contract this extends
[^vector-orientation]: gotchas/ecco-vector-orientation.md
