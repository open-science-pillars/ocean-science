---
type: dataset-gotcha
title: "ECCO budgets and transports close only on the native llc90 grid"
description: "The interpolated 0.5 degree ECCO product does not conserve; budgets computed on it fail closure by construction, and the flux ingredients do not exist there."
tags: [ecco, budgets, regridding, llc90]
timestamp: 2026-07-04
severity: high
dataset: ../datasets/ecco-v4r4.md
eval_case: native-grid-refusal
# eval case authored in Session 8b per SPEC §4.1; id fixed here so the
# linter's dangling check closes when the case lands.
evidence:
  - https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Heat_budget_closure.html
  - https://podaac.jpl.nasa.gov/dataset/ECCO_L4_TEMP_SALINITY_05DEG_MONTHLY_V4R4
  - ../../skills/ecco/references/budget-formulation.md
status: verified
verified: 2026-07-04
verified_by: Paul Ramirez (steward pro tem)
---

# ECCO budgets and transports close only on the native llc90 grid

**Mechanism.** ECCO's conservation is a property of the native
formulation: face fluxes (ADV*, DF*), partial-cell geometry (hFac), and
tile topology together satisfy the model equations exactly. The 0.5
degree `05DEG` collections are produced by interpolation for display
and comparison convenience; interpolation does not preserve flux
divergences, and the budget ingredients (3D flux collections, hFac
geometry) exist only for the llc90 collections. The ECCO v4 budget
tutorial builds every term from native-grid products.

**Wrong-result mode.** A "heat budget" assembled from regridded fields
produces residuals of the same order as the physical terms; tendencies
attributed to mixing or forcing are numerical artifacts of the
interpolation. Nothing errors; the numbers are simply wrong.

**Correct approach.** Budgets and transports are computed on the native
grid with tile-aware operators and the geometry granule merged in
(formulation per the linked reference, verified against the ECCO
tutorial 2026-07-04). Regridded fields serve for maps and pointwise
comparison against gridded observations. No correct budget formulation
exists on regridded ECCO; the native-grid path is the only valid route.
(Refusal of regridded-budget requests is workflow behavior owned by the
ocean-budget skill, which cites this concept when it declines.)

**Verification.** The `05DEG` collections carry state variables only
(CMR sweep 2026-07-04 found no 05DEG 3D flux collections), so the
native formulation is not even assemblable from them; the tutorial's
closure demonstration is native-grid throughout.
