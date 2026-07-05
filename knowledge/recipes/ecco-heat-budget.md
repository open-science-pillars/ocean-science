---
type: recipe
title: "Closed heat budget on the ECCO v4r4 native grid"
description: "Validated pattern for the four-term heat budget with the machine-precision residual expectation."
tags: [ecco, heat-budget, closure, native-grid]
timestamp: 2026-07-04
inputs:
  - dataset: ../datasets/ecco-v4r4.md
  - collections: "ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX (monthly), ECCO_L4_HEAT_FLUX (monthly), ECCO_L4_TEMP_SALINITY (snapshots), ECCO_L4_SSH (snapshots, ETAN), geometry granule"
  - ancillary: "geothermalFlux.bin from the ECCO tutorial misc directory (not a PO.DAAC collection)"
  - method: "four terms exactly per skills/ecco/references/budget-formulation.md (tutorial-quoted, verified 2026-07-04)"
expected:
  - quantity: "pointwise residual, tendency minus (advection + diffusion + forcing)"
    statement: "machine precision for float32 fields: relative residual against the dominant term at or below 1e-6 at every wet cell, every month; the tutorial's closure demonstration shows order 1e-9"
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
fields); the budget-closure skill carries the diagnosis discipline and
the budget-auditor agent reviews every budget after computation.
