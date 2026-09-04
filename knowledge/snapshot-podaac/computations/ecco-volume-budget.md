---
type: Attested Computation
title: "Volume budget closure on the ECCO v4r4 native grid (attested, draft)"
description: "Draft contract for the attested volume budget; the sanctioned computation is not yet extracted from the volume_budget golden."
tags: [ecco, volume-budget, closure, attested, native-grid, freshwater]
runtime: python
parameters:
  - { name: year, type: integer, required: true }
  - { name: region, type: string, required: false }
generated: { by: claude-code/fable-5, at: 2026-08-30T19:20:00Z }
status: draft
---

# Volume budget closure on the ECCO v4r4 native grid (attested, draft)

Draft skeleton following [the attested heat budget](ecco-heat-budget.md).
The narrative recipe is [ecco-volume-budget](../recipes/ecco-volume-budget.md);
until extraction lands, that recipe still owns the pass bar (golden
asserts max at or below 1e-11 1/s, p99.9 at or below 1e-12).

# Computation

Stub, not yet sanctioned: to be extracted from the ocean-science golden
`verification/volume_budget.py` (extraction only, no new numerics), with
`executor` and `attester` fields and receipt emission. Contract point
worth attesting: the budget closes on transport convergence ALONE
(`WVELMASS` already carries the surface freshwater flux); a run with an
`oceFWflx` forcing term added is the natural sabotage beat, driving the
surface residual to order 1e-8.
