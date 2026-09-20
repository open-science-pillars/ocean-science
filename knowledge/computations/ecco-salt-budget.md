---
type: Attested Computation
spheres: [hydrosphere]
title: "Salt budget closure on the ECCO v4r4 native grid (attested, draft)"
description: "Draft contract for the attested salt budget; the sanctioned computation is not yet extracted from the salt_budget golden."
tags: [ecco, salt-budget, closure, attested, native-grid]
runtime: python
parameters:
  - { name: year, type: integer, required: true }
  - { name: region, type: string, required: false }
generated: { by: claude-code/fable-5, at: 2026-08-30T19:20:00Z }
executor:
status: draft
---

# Salt budget closure on the ECCO v4r4 native grid (attested, draft)

**Placement, 2026-09-20 (ADR E, a computation is a skill).** This
concept came from the nasa-daac-knowledge bundle at
`knowledge/podaac/computations/ecco-salt-budget.md`, and it names no
executor. This concept names no executor yet, so there is no reference
run to re-run; the retired `executor.skill` key is gone and nothing
takes its place until the computation is extracted. The signature block
is the one the maintainer left; the concept sits at `status: draft` with
no verified event added, and the maintainer re-signs it after merge.

Draft skeleton following [the attested heat budget](ecco-heat-budget.md):
the same contract shape (declared parameters, receipt, deterministic
attester) applied to the four-term salt budget. The narrative recipe is
[ecco-salt-budget](knowledge/podaac/recipes/ecco-salt-budget.md); until extraction
lands, that recipe still owns the pass bar (golden asserts max at or
below 1.5e-10 g/kg/s, p99.9 at or below 2e-11).

# Computation

Stub, not yet sanctioned: to be extracted from the ocean-science golden
`verification/salt_budget.py` the way the heat budget was (extraction
only, no new numerics), together with `executor` and `attester` fields
and receipt emission. Salt-specific contract points: `oceSPtnd` brine
plume plus surface `SFLUX` forcing, no shortwave, no geothermal.
