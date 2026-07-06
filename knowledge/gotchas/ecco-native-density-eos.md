---
type: dataset-gotcha
title: "ECCO density and stratification come from its own equation of state; a foreign EOS makes phantom differences"
description: "ECCO ships in-situ density anomaly (RHOAnoma) and the vertical density gradient (DRHODR) from the model's own equation of state; recomputing density or stratification from THETA and SALT with a different EOS produces artifacts that corrupt density-space water-mass boundaries and any stratification or budget diagnostic."
tags: [ecco, density, eos, stratification, water-masses]
timestamp: 2026-07-05
severity: high
dataset: ../datasets/ecco-v4r4.md
status: verified
verified: 2026-07-06
verified_by: OSP steward review
evidence:
  - https://www.teos-10.org/
---

# ECCO density and stratification come from its own equation of state; a foreign EOS makes phantom differences

**Mechanism.** ECCO integrates the ocean with a specific equation of
state and ships the resulting fields in its density collection: the
in-situ density anomaly (`RHOAnoma`) and the vertical density gradient
(`DRHODR`). These are consistent with the model's temperature and
salinity (`THETA`, `SALT`; flavor identity owned by
[ecco-v4r4](../datasets/ecco-v4r4.md)) and with the model's budgets and
stratification. They are the product's own answer for density, not a
post-hoc estimate.

**Wrong-result mode.** Recomputing density or stratification from
`THETA` and `SALT` with a different equation of state (a generic
gsw/TEOS-10 call, or a different reference pressure) yields values that
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
