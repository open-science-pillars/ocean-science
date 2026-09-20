---
type: Attested Computation
spheres: [hydrosphere]
title: "Meridional heat transport at 26.5N from ECCO v4r4 (attested, draft)"
description: "Draft contract for the attested MHT computation; the sanctioned computation is not yet extracted from the transport_analysis golden."
tags: [ecco, mht, transport, rapid, attested]
runtime: python
parameters:
  - { name: year, type: integer, required: true }
  - { name: basin, type: string, required: false }
generated: { by: claude-code/fable-5, at: 2026-08-30T19:20:00Z }
executor:
status: draft
---

# Meridional heat transport at 26.5N from ECCO v4r4 (attested, draft)

**Placement, 2026-09-20 (ADR E, a computation is a skill).** This
concept came from the nasa-daac-knowledge bundle at
`knowledge/podaac/computations/ecco-mht-26n.md`, and it names no
executor. This concept names no executor yet, so there is no reference
run to re-run; the retired `executor.skill` key is gone and nothing
takes its place until the computation is extracted. The signature block
is the one the maintainer left; the concept sits at `status: draft` with
no verified event added, and the maintainer re-signs it after merge.

Draft skeleton following [the attested heat budget](ecco-heat-budget.md).
The narrative recipe is [ecco-mht-26n](knowledge/podaac/recipes/ecco-mht-26n.md), which
owns the anchors until extraction lands (2010: Atlantic atlExt 0.666 PW;
global circle 1.098 PW equal to the basin sum) and the scope discipline
(`basin` unset means the FULL latitude circle, never a RAPID-comparable
number).

# Computation

Stub, not yet sanctioned: to be extracted from the ocean-science golden
`verification/transport_analysis.py` (extraction only, no new numerics),
with `executor` and `attester` fields and receipt emission. The receipt
wants the bound `basin` echoed back so the attester can refuse a
global-circle value presented against RAPID (the ecco-mht-basin-scope
gotcha as a mechanical check).
