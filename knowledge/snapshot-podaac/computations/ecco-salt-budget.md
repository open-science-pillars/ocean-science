---
type: Attested Computation
title: "Salt budget closure on the ECCO v4r4 native grid (attested, draft)"
description: "Draft contract for the attested salt budget; the sanctioned computation is not yet extracted from the salt_budget golden."
tags: [ecco, salt-budget, closure, attested, native-grid]
runtime: python
parameters:
  - { name: year, type: integer, required: true }
  - { name: region, type: string, required: false }
generated: { by: claude-code/fable-5, at: 2026-08-30T19:20:00Z }
status: draft
---

# Salt budget closure on the ECCO v4r4 native grid (attested, draft)

Draft skeleton following [the attested heat budget](ecco-heat-budget.md):
the same contract shape (declared parameters, receipt, deterministic
attester) applied to the four-term salt budget. The narrative recipe is
[ecco-salt-budget](../recipes/ecco-salt-budget.md); until extraction
lands, that recipe still owns the pass bar (golden asserts max at or
below 1.5e-10 g/kg/s, p99.9 at or below 2e-11).

# Computation

Stub, not yet sanctioned: to be extracted from the ocean-science golden
`verification/salt_budget.py` the way the heat budget was (extraction
only, no new numerics), together with `executor` and `attester` fields
and receipt emission. Salt-specific contract points: `oceSPtnd` brine
plume plus surface `SFLUX` forcing, no shortwave, no geothermal.
