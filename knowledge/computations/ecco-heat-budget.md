---
type: Attested Computation
spheres: [hydrosphere]
title: "Heat budget closure on the ECCO v4r4 native grid (attested)"
description: "Sanctioned four-term heat budget computation; a run passes attestation only within the recorded residual tolerances on unmodified code."
tags: [ecco, heat-budget, closure, attested, native-grid]
runtime: python
parameters:
  - { name: year, type: integer, required: true }
  - { name: region, type: string, required: false }
computation: skills/ocean-budget/scripts/ecco_heat_budget.py
executor:
  resource: skills/ocean-budget/scripts/ecco_heat_budget.py
  receipt: [run_id, code_sha256, data, bound_parameters, residual_max, residual_p999, cells_evaluated]
attester:
  resource: skills/ocean-budget/scripts/budget_residual.py
generated: { by: claude-code/fable-5, at: 2026-08-30T19:20:00Z }
verified:
  - { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
  - { by: human:PaulMRamirez, at: 2026-09-05T20:22:37Z }
  - { by: human:PaulMRamirez, at: 2026-09-16T05:51:09Z, role: maintainer, source: https://github.com/open-science-pillars/nasa-daac-knowledge/pull/183 }
status: draft
sources:
  - id: budget-formulation
    resource: knowledge/podaac/conventions/ecco-budget-formulation.md
    title: "Bundle convention: ECCO v4r4 budget formulation on the native grid"
  - id: attester
    resource: skills/ocean-budget/scripts/budget_residual.py
    title: "The deterministic attester: the pass bar it enforces, recorded with its 2x headroom over the measured max"
  - id: readthedocs-ecco-v4-heat-budget-closure
    resource: https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Heat_budget_closure.html
    title: "ECCO v4 Python tutorial: heat budget closure notebook"
    author: team:ecco-consortium
---

# Heat budget closure on the ECCO v4r4 native grid (attested)

**Placement, 2026-09-20 (ADR E, a computation is a skill).** This
concept came from the nasa-daac-knowledge bundle at
`knowledge/podaac/computations/ecco-heat-budget.md`, and the executor
and the attester it names now ship in this package under
`skills/ocean-budget/scripts/`. The golden
`verification/ocean_budget.py` names every script it does. The executor
`skills/ocean-budget/scripts/ecco_heat_budget.py` changed only where it
resolves a path, so its sha256 moved from 05de42d3ff95f0c5 to
2e4a6c66cc4467c1 and no number in it did. The reference run
`heat-budget` reads the ECCO 2010 fixture cache, which this environment
does not hold, so it was not re-run here; the golden runs it where the
cache is present. The signature block is the one the maintainer left;
the concept sits at `status: draft` with no verified event added, and
the maintainer re-signs it after merge.

The sanctioned computation lives at the `computation:` path (file form,
OKF v0.2 §10.3): the four-term budget, tendency minus (advection + diffusion +
forcing), exactly as the [budget formulation convention](knowledge/podaac/conventions/ecco-budget-formulation.md)
records from the ECCO v4 tutorial,[^budget-formulation][^readthedocs-ecco-v4-heat-budget-closure]
extracted 2026-08-30 from the ocean-science golden notebook
(`verification/ocean_budget.py`) with parameter binding and receipt
emission added and no numerical change. The narrative recipe
([ecco-heat-budget](knowledge/podaac/recipes/ecco-heat-budget.md)) explains the
formulation and the tolerance rationale; this concept owns the pass bar.

## Pass bar (the attested tolerances)

A run PASSES attestation only when, on unmodified sanctioned code with
only declared parameters bound:

- `residual_max` at or below 1e-10 degC/s (absolute, pointwise, every
  wet cell, every month), and
- `residual_p999` at or below 1e-11 degC/s.

Baseline measurement (2026-07-04, year 2010, region tile1-interior,
3,341,772 cell-months): max 4.95e-11, p99.9 7.3e-12, median 5.7e-14
degC/s; the tolerance carries 2x headroom over the measured
max.[^attester]

## Parameters

- `year` (integer, required): the calendar year the budget closes over;
  12 monthly means bracketed by 13 month-boundary snapshots.
- `region` (string, optional, default `tile1-interior`): named spatial
  subset. `tile1-interior` is the fixture-verified subset; pointwise
  closure holds on any spatial subset (the recipe's domain caveat).

## Execution and attestation

The executor (`executor.resource`) stages the fixture cache, runs the
computation with the bound parameters, and collects the declared receipt
fields. The attester (`attester.resource`) is deterministic, stdlib-only
code: PASS requires the receipt's `code_sha256` to equal the sha256 of
the sanctioned computation file, `bound_parameters` to match the declared
set above, and both residuals within the pass bar. A rewritten
computation, an undeclared parameter, or a formulation error (a dropped
geothermal term drives deep-cell residuals orders above
tolerance[^budget-formulation]) fails mechanically.

**Data provenance.** The receipt also carries a `data` block: the data
root and the `RECORD.json` stamp the verify tool leaves in a tree it has
checked against its manifest (record name, manifest SHA-256,
verification time, report SHA-256). The attester refuses a receipt
whose `data.record` is not that stamp, so nothing is attested against a
tree this bundle has not manifested and verified. The two trees and
the rule are in docs/science-record.md.

[^budget-formulation]: Bundle convention: ECCO v4r4 budget formulation on the native grid
[^attester]: The deterministic attester: the pass bar it enforces, recorded with its 2x headroom over the measured max
[^readthedocs-ecco-v4-heat-budget-closure]: ECCO v4 Python tutorial: heat budget closure notebook
