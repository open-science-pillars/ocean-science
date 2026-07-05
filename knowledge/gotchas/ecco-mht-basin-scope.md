---
type: dataset-gotcha
title: "ECCO meridional heat transport: no basin mask means the full latitude circle"
description: "calc_meridional_heat_trsp without a basin_name integrates the whole latitude circle (Atlantic + Pacific + Indian), not the Atlantic section RAPID observes."
tags: [ecco, mht, heat-transport, basin, rapid, scope]
timestamp: 2026-07-05
severity: high
dataset: ../datasets/ecco-v4r4.md
eval_case: mht-basin-scope
evidence:
  - ../recipes/ecco-mht-26n.md
  - https://github.com/open-science-pillars/ocean-science/blob/main/skills/ecco/references/variable-catalog.md
status: verified
verified: 2026-07-05
verified_by: OSP steward review
---

# ECCO meridional heat transport: no basin mask means the full latitude circle

**Mechanism.** `calc_meridional_heat_trsp(ds, lat_vals=26.5)` with no
`basin_name` integrates the FULL latitude circle (Atlantic plus Pacific
plus Indian). The RAPID/MOCHA array observes the ATLANTIC section only,
which requires `basin_name="atlExt"` (and the ecco_v4_py binary basin
masks present in the environment).

**Wrong-result mode.** Comparing the no-mask value against RAPID is a
scope error: it compares a global-circle quantity against an
Atlantic-only observation. Measured on ECCO v4r4 2010 (recipe
provenance): the global circle mean is 1.098 PW, which equals the basin
sum (atlExt 0.666 + pacExt 0.430 + indExt 0.002), while the
RAPID-comparable Atlantic mean is 0.666 PW. Quoting 1.098 PW as "the
26.5N heat transport" against a ~1.3 PW RAPID mean invents a
disagreement in one direction and hides the real Atlantic offset in the
other.

**Correct approach.** Every MHT number names its scope (basin or full
circle); RAPID comparisons use the atlExt-masked value; the full-circle
number is used only as a method-reproducibility check (it must equal
the basin sum).

**Verification.** Reproducible from the recipe's recorded 2010 basin
decomposition (the three basins sum to the no-mask value exactly);
`knowledge/recipes/ecco-mht-26n.md` carries the expected values and the
comparison discipline.
