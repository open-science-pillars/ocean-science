---
type: recipe
title: "Closed heat budget on the ECCO v4r4 native grid"
description: "Validated pattern for the four-term heat budget with the machine-precision residual expectation."
tags: [ecco, heat-budget, closure, native-grid]
timestamp: 2026-07-04
inputs:
  - dataset: ../datasets/ecco-v4r4.md
  - collections: "ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_MONTHLY_V4R4, ECCO_L4_HEAT_FLUX_LLC0090GRID_MONTHLY_V4R4, ECCO_L4_TEMP_SALINITY_LLC0090GRID_SNAPSHOT_V4R4, ECCO_L4_SSH_LLC0090GRID_SNAPSHOT_V4R4 (ETAN), ECCO_L4_GEOMETRY_LLC0090GRID_V4R4"
  - ancillary: "geothermalFlux.bin from the ECCO tutorial misc directory (not a PO.DAAC collection)"
  - method: "four terms exactly per skills/ecco/references/budget-formulation.md (tutorial-quoted, verified 2026-07-04)"
expected:
  - quantity: "pointwise residual, tendency minus (advection + diffusion + forcing)"
    statement: "pass tolerance: ABSOLUTE residual at or below 1e-10 degC/s at every wet cell, every month, with p99.9 at or below 1e-11. Measured 2026-07-04 on the 2010 tile-interior subset (3.34 million cell-months): max 4.95e-11, p99.9 7.3e-12, median 5.7e-14 degC/s; the tolerance carries 2x headroom over the measured max"
  - quantity: "why the criterion is absolute, not relative"
    statement: "the archive stores float32; the measured residual is storage quantization (median 0.15x the snapshot quantization floor, 99.6% of cells within 3x it). Relative-to-dominant-term ratios are meaningful only where terms exceed that floor; in quiescent deep cells the ratio measures quantization, not formulation error (ratios up to 9e-2 observed on a correct formulation)"
expected_uncertainty:
  - quantity: "numerical tolerance"
    statement: "the residual expectation IS the uncertainty statement for this identity: pass at relative 1e-6, investigate above it using the formulation traps table (residual signatures map to specific omissions); closure failure is a formulation error, never data noise"
  - quantity: "domain caveat"
    statement: "pointwise closure holds on any spatial subset; domain-integrated closure holds only on closed domains with boundary transports accounted (SPEC §6 encodes this for fixtures)"
evidence:
  - https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Heat_budget_closure.html
  - ../../skills/ecco/references/budget-formulation.md
status: verified
verified: 2026-07-04
verified_by: Paul Ramirez (steward pro tem)
---

# Closed heat budget on the ECCO v4r4 native grid

The validated pattern: assemble tendency (snapshots with the z* scale
factor), advective convergence (tile-aware differencing of ADV fluxes),
diffusive convergence (explicit plus implicit vertical), and forcing
(TFLUX with shortwave penetration to 200 m, geothermal at the bottom
wet cell), exactly as the budget-formulation reference quotes from the
ECCO v4 tutorial (verified line by line 2026-07-04). Volume element
rA * drF * hFacC; constants rhoconst 1029, c_p 3994.

**Validation provenance.** The ECCO v4 Python tutorial's closure
notebook demonstrates the residual at machine precision globally (the
evidence link); this org's line-by-line verification of the formulation
against that notebook is recorded in the budget-formulation reference.
The durable executable validation is the Session 9 golden notebook
`verification/ocean_budget.py`, which asserts pointwise closure on
fixture cells against this recipe's tolerance.

**Diagnosis on failure.** The budget-formulation traps table maps
residual signatures to omissions (geothermal, z*, implicit diffusion,
double hFac, monthly-mean bookends, seam differencing, regridded
fields). (Diagnosis discipline and post-computation review are
workflow behavior owned by the budget-closure skill and the
budget-auditor agent, not by this concept.)
