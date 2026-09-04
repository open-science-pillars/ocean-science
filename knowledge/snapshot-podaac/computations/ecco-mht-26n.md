---
type: Attested Computation
title: "Meridional heat transport at 26.5N from ECCO v4r4 (attested, draft)"
description: "Draft contract for the attested MHT computation; the sanctioned computation is not yet extracted from the transport_analysis golden."
tags: [ecco, mht, transport, rapid, attested]
runtime: python
parameters:
  - { name: year, type: integer, required: true }
  - { name: basin, type: string, required: false }
generated: { by: claude-code/fable-5, at: 2026-08-30T19:20:00Z }
status: draft
---

# Meridional heat transport at 26.5N from ECCO v4r4 (attested, draft)

Draft skeleton following [the attested heat budget](ecco-heat-budget.md).
The narrative recipe is [ecco-mht-26n](../recipes/ecco-mht-26n.md), which
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
