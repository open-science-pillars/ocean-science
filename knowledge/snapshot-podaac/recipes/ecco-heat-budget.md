---
type: recipe
title: "Closed heat budget on the ECCO v4r4 native grid"
description: "Validated pattern for the four-term heat budget with the machine-precision residual expectation."
tags: [ecco, heat-budget, closure, native-grid]
generated: { by: knowledge-seeder/claude, at: 2026-07-04T00:00:00Z }
inputs:
  - dataset: ../datasets/ecco-v4r4.md
  - collections: "ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX_LLC0090GRID_MONTHLY_V4R4, ECCO_L4_HEAT_FLUX_LLC0090GRID_MONTHLY_V4R4, ECCO_L4_TEMP_SALINITY_LLC0090GRID_SNAPSHOT_V4R4, ECCO_L4_SSH_LLC0090GRID_SNAPSHOT_V4R4 (ETAN), ECCO_L4_GEOMETRY_LLC0090GRID_V4R4"
  - ancillary: "geothermalFlux.bin from the ECCO tutorial misc directory (not a PO.DAAC collection)"
  - method: "four terms exactly per ../conventions/ecco-budget-formulation.md (tutorial-quoted, verified 2026-07-04)"
expected:
  - quantity: "pointwise residual, tendency minus (advection + diffusion + forcing)"
    statement: "the pass bar (absolute pointwise tolerances and the 2026-07-04 baseline measurement) is owned by the attested computation concept ../computations/ecco-heat-budget.md; a run counts only when its receipt passes that concept's deterministic attester"
  - quantity: "why the criterion is absolute, not relative"
    statement: "the archive stores float32; the measured residual sits at the storage quantization scale, where the floor is one unit in the last place of the stored snapshot tendency divided by the snapshot interval (measured over the 3,341,772 baseline cell-months: median residual 0.66x that floor, 96.4 percent of cells within 3x, 99.7 percent within 10x; derivation in references/derivations/quantization_floor.py). Relative-to-dominant-term ratios are meaningful only where terms exceed that floor; in quiescent deep cells the ratio measures quantization, not formulation error (ratios up to 9e-2 observed on a correct formulation)"
expected_uncertainty:
  - quantity: "numerical tolerance"
    statement: "the residual expectation IS the uncertainty statement for this identity: pass within the attested computation concept's tolerances (../computations/ecco-heat-budget.md), investigate above them using the formulation traps table (residual signatures map to specific omissions); closure failure is a formulation error, never data noise"
  - quantity: "domain caveat"
    statement: "pointwise closure holds on any spatial subset; domain-integrated closure holds only on closed domains with boundary transports accounted (SPEC §6 encodes this for fixtures)"
sources:
  - id: readthedocs-ecco-v4-heat-budget-closure
    resource: https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Heat_budget_closure.html
    title: "ECCO v4 Python tutorial: heat budget closure notebook"
    author: team:ecco-consortium
  - id: budget-formulation
    resource: ../conventions/ecco-budget-formulation.md
    title: "Bundle convention: ECCO v4r4 budget formulation on the native grid"
status: stable
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
stale_after: 2027-01-04
---

# Closed heat budget on the ECCO v4r4 native grid

The validated pattern: assemble tendency (snapshots with the z* scale
factor), advective convergence (tile-aware differencing of ADV fluxes),
diffusive convergence (explicit plus implicit vertical), and forcing
(TFLUX with shortwave penetration to 200 m, geothermal at the bottom
wet cell), exactly as the [budget formulation convention](../conventions/ecco-budget-formulation.md)
records from the ECCO v4 tutorial (verified line by line 2026-07-04).[^budget-formulation][^readthedocs-ecco-v4-heat-budget-closure] Volume element
rA * drF * hFacC; constants rhoconst 1029, c_p 3994.

**Validation provenance.** The ECCO v4 Python tutorial's closure
notebook demonstrates the residual at machine precision globally (the
evidence link)[^readthedocs-ecco-v4-heat-budget-closure]; the line-by-line verification of the formulation
against that notebook is recorded in the budget formulation convention and
carried verbatim by the sanctioned computation.[^budget-formulation]
The durable executable validation is the golden notebook
`verification/ocean_budget.py`; the sanctioned, attestable form is
[the attested computation concept](../computations/ecco-heat-budget.md),
which owns the pass-bar numbers and the deterministic attester (OKF
v0.2 section 10, Appendix A pattern).

**Diagnosis on failure.** The formulation convention's traps table maps
residual signatures to omissions (geothermal, z*, implicit diffusion,
double hFac, monthly-mean bookends, seam differencing, regridded
fields).[^budget-formulation] (Diagnosis discipline and post-computation review are
workflow behavior owned by the budget-closure skill and the
budget-auditor agent, not by this concept.)

[^readthedocs-ecco-v4-heat-budget-closure]: ECCO v4 Python tutorial: heat budget closure notebook
[^budget-formulation]: Bundle convention: ECCO v4r4 budget formulation on the native grid
