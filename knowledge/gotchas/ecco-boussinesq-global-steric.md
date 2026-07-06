---
type: dataset-gotcha
title: "ECCO is Boussinesq: global-mean steric sea level needs the mass-conservation correction"
description: "Boussinesq models conserve volume, not mass; ECCO's global-mean steric sea level needs the standard global (Greatbatch) correction before global budgets, though regional patterns are unaffected."
tags: [ecco, boussinesq, steric, global-mean, sea-level, greatbatch]
timestamp: 2026-07-05
severity: medium
# medium pending steward calibration: this bites only the global-mean
# scalar (regional patterns are unaffected), but there it is silently
# wrong without the correction; the steward may promote to high, which
# then requires the matching eval case (harness rule 9).
dataset: ../datasets/ecco-v4r4.md
evidence:
  - https://doi.org/10.1029/94JC00847
status: verified
verified: 2026-07-06
verified_by: OSP steward review
---

# ECCO is Boussinesq: global-mean steric sea level needs the mass-conservation correction

**Mechanism.** ECCO runs the MITgcm in Boussinesq mode, which conserves
volume rather than mass. A Boussinesq ocean therefore does not represent
global-mean steric (thermosteric) sea level change directly: the
global-mean expansion signal must be added back through the standard
global correction (the Greatbatch adjustment) before the number is used
in a global budget.

**Wrong-result mode.** Quoting ECCO's global-mean sea level or global
steric change without the mass-conservation correction reports a global
number that is silently wrong; the omission does not error and the field
looks complete.

**Correct approach.** Apply the standard global (Greatbatch) correction
to the global-mean steric term before any global sea level budget, and
state that it was applied. Regional sea level patterns are unaffected by
this correction, so a regional analysis does not need it; the trap is
specifically the global mean. This term is part of the sea level budget
bookkeeping
([sea-level-budget-closure](../conventions/sea-level-budget-closure.md)).

**Verification.** The Boussinesq volume-conservation property and the
need for the global steric correction are standard for the MITgcm
configuration ECCO uses; the correction changes only the global-mean
scalar, which is checkable by confirming the regional pattern is
unchanged when it is applied.
