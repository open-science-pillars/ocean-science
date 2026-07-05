---
type: dataset-gotcha
title: "ECCO heat budgets need the geothermal flux, which is not a PO.DAAC collection"
description: "Deep and full-depth ECCO heat budgets fail closure unless the static geothermal flux ancillary field is added at the bottom wet cell."
tags: [ecco, heat-budget, geothermal, ancillary]
timestamp: 2026-07-04
severity: high
dataset: ../datasets/ecco-v4r4.md
eval_case: geothermal-omission
# eval case authored per SPEC §4.1; id fixed here so the
# linter's dangling check closes when the case lands.
evidence:
  - https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Heat_budget_closure.html
  - https://github.com/ECCO-GROUP/ECCO-v4-Python-Tutorial/blob/master/misc/geothermalFlux.bin
  - https://github.com/open-science-pillars/ocean-science/blob/main/skills/ecco/references/budget-formulation.md
status: verified
verified: 2026-07-04
verified_by: OSP steward review
---

# ECCO heat budgets need the geothermal flux, which is not a PO.DAAC collection

**Mechanism.** The ECCO v4 forcing includes a static geothermal heat
flux applied at the bottom wet cell of every column. It is a model
input, not an output diagnostic: no PO.DAAC collection carries it. The
tutorial reads the binary ancillary file (`geothermalFlux.bin`, in the
tutorial repository's misc directory) with `read_llc_to_tiles` and
builds the 3D field with a bottom-cell mask
(`mskb = mskC - mskC.shift(k=-1)`).

**Wrong-result mode.** A heat budget assembled from PO.DAAC collections
alone omits the term silently: surface layers close, deep and bottom
cells fail by order 10 to 100 mW m-2 equivalent, and full-depth column
budgets carry the same bias everywhere. The signature (closure that
degrades with depth and concentrates at the seafloor) is the first
thing to check on any ECCO heat-budget residual.

**Correct approach.** Fetch the ancillary file, build the bottom-masked
3D field, and add it to the surface forcing before the unit conversion,
exactly as the budget-formulation reference quotes from the tutorial
(term 4, verified line by line 2026-07-04). Salt and volume budgets do
not carry a geothermal term; this is heat-budget specific.

**Verification.** The linked tutorial's forcing section constructs
GEOFLX and includes it in G_forcing; its closure demonstration fails
without the term (the traps table in the budget-formulation reference
records the signature).
