---
type: Attested Computation
title: "Heat budget closure on the ECCO v4r4 native grid (attested)"
description: "Sanctioned four-term heat budget computation; a run passes attestation only within the recorded residual tolerances on unmodified code."
tags: [ecco, heat-budget, closure, attested, native-grid]
runtime: python
parameters:
  - { name: year, type: integer, required: true }
  - { name: region, type: string, required: false }
computation: references/computations/ecco_heat_budget.py
executor:
  resource: references/skills/run-golden.md
  receipt: [run_id, code_sha256, bound_parameters, residual_max, residual_p999, cells_evaluated]
attester:
  resource: references/attesters/budget_residual.py
generated: { by: claude-code/fable-5, at: 2026-08-30T19:20:00Z }
status: draft
sources:
  - id: github-budget-formulation
    resource: https://github.com/open-science-pillars/ocean-science/blob/main/skills/ecco/references/budget-formulation.md
    title: "OSP ocean-science reference: ECCO v4r4 heat budget formulation (native grid)"
    author: human:PaulMRamirez
  - id: readthedocs-ecco-v4-heat-budget-closure
    resource: https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Heat_budget_closure.html
    title: "ECCO v4 Python tutorial: heat budget closure notebook"
    author: team:ecco-consortium
---

# Heat budget closure on the ECCO v4r4 native grid (attested)

The sanctioned computation lives at the `computation:` path (file form,
spec 10.3): the four-term budget, tendency minus (advection + diffusion +
forcing), exactly as the budget-formulation reference quotes from the
ECCO v4 tutorial,[^github-budget-formulation][^readthedocs-ecco-v4-heat-budget-closure]
extracted 2026-08-30 from the ocean-science golden notebook
(`verification/ocean_budget.py`) with parameter binding and receipt
emission added and no numerical change. The narrative recipe
([ecco-heat-budget](../recipes/ecco-heat-budget.md)) explains the
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
max.[^github-budget-formulation]

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
tolerance[^github-budget-formulation]) fails mechanically.

[^github-budget-formulation]: OSP ocean-science reference: ECCO v4r4 heat budget formulation (native grid)
[^readthedocs-ecco-v4-heat-budget-closure]: ECCO v4 Python tutorial: heat budget closure notebook
