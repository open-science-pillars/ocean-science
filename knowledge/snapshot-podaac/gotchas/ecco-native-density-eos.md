---
type: dataset-gotcha
title: "ECCO density and stratification come from its own equation of state; a foreign EOS makes phantom differences"
description: "ECCO ships in-situ density anomaly (RHOAnoma) and the vertical density gradient (DRHODR) from the model's own equation of state; recomputing density or stratification from THETA and SALT with a different EOS produces artifacts that corrupt density-space water-mass boundaries and any stratification or budget diagnostic."
tags: [ecco, density, eos, stratification, water-masses]
generated: { by: claude-code/opus-4.8, at: 2026-07-05T00:00:00Z }
severity: high
dataset: ../datasets/ecco-v4r4.md
sources:
  - id: dens-strat-granule
    resource: https://doi.org/10.5067/ECL5M-ODE44
    title: "ECCO Ocean Density, Stratification, and Hydrostatic Pressure, monthly mean llc90 (ECCO_L4_DENS_STRAT_PRESS_LLC0090GRID_MONTHLY_V4R4); the RHOAnoma and DRHODR variable attributes, read from the 2009-12 granule on 2026-09-04"
  - id: teos-10
    resource: https://www.teos-10.org/
    title: "TEOS-10, the international thermodynamic equation of seawater and its Gibbs SeaWater toolbox; the equation of state a generic recomputation reaches for"
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
status: stable
stale_after: 2027-03-04
---

# ECCO density and stratification come from its own equation of state; a foreign EOS makes phantom differences

**Mechanism.** ECCO integrates the ocean with a specific equation of
state and ships the resulting fields in its density collection: the
in-situ density anomaly (`RHOAnoma`) and the vertical density gradient
(`DRHODR`). These are consistent with the model's temperature and
salinity (`THETA`, `SALT`; flavor identity owned by
[ecco-v4r4](../datasets/ecco-v4r4.md)) and with the model's budgets and
stratification. They are the product's own answer for density, not a
post-hoc estimate. The granule attributes state the equation of state:
a modified UNESCO formula (Jackett and McDougall 1995) driven by the
model's potential temperature under a horizontally and temporally
constant pressure; `RHOAnoma` is the in-situ density anomaly relative
to `rhoConst` = 1029 kg m-3, and `DRHODR` is d(sigma)/dz computed from
in-situ density.[^dens-strat-granule]

**Wrong-result mode.** Recomputing density or stratification from
`THETA` and `SALT` with a different equation of state (a generic
gsw/TEOS-10 call,[^teos-10] or a different reference pressure) yields values that
differ from the model's own by amounts comparable to the stratification
signal under study. Water-mass boundaries in density space shift,
apparent stratification and neutral surfaces move, and any diagnostic
that must stay consistent with ECCO's budgets (buoyancy forcing,
water-mass transformation) picks up a phantom term. Nothing errors; the
numbers are simply inconsistent with the model.

**Correct approach.** When budgets or stratification are in play, use
ECCO's shipped density fields (`RHOAnoma`, `DRHODR`) rather than
recomputing with a foreign EOS. If a derived density surface is
unavoidable, use one equation of state and reference pressure
consistently across the entire study, state which, and do not mix it
with the shipped fields on the same analysis. For pure relative-structure
classification a single consistent foreign EOS may be acceptable, but
the choice is recorded in methods.

**Verification.** Pending: a steward must attach a reproducing check
(recomputed-vs-shipped density difference on a stratified column) and a
verifiable evidence link, and author the severity-matched eval case, before
this draft is promoted to verified.

[^dens-strat-granule]: ECCO_L4_DENS_STRAT_PRESS_LLC0090GRID_MONTHLY_V4R4, doi:10.5067/ECL5M-ODE44, RHOAnoma and DRHODR attributes of the 2009-12 granule
[^teos-10]: TEOS-10 and the Gibbs SeaWater toolbox, teos-10.org
