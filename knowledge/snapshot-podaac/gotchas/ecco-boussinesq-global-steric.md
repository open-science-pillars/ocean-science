---
type: dataset-gotcha
title: "ECCO is Boussinesq: global-mean steric sea level needs the mass-conservation correction"
description: "Boussinesq models conserve volume, not mass; ECCO's global-mean steric sea level needs the standard global (Greatbatch) correction before global budgets, though regional patterns are unaffected."
tags: [ecco, boussinesq, steric, global-mean, sea-level, greatbatch]
generated: { by: claude-code/opus-4.8, at: 2026-07-05T00:00:00Z }
severity: medium
# medium pending steward calibration: this bites only the global-mean
# scalar (regional patterns are unaffected), but there it is silently
# wrong without the correction; the steward may promote to high, which
# then requires the matching eval case.
dataset: ../datasets/ecco-v4r4.md
sources:
  - id: greatbatch-1994
    resource: https://doi.org/10.1029/94JC00847
    title: "Greatbatch (1994), A note on the representation of steric sea level in models that conserve volume rather than mass, Journal of Geophysical Research: Oceans 99(C6)"
  - id: steric-computation
    resource: ../computations/ecco-steric-height.md
    title: "The attested steric height computation: a global run cannot pass attestation without the Boussinesq caveat field in its receipt"
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
status: stable
stale_after: 2027-03-04
---

# ECCO is Boussinesq: global-mean steric sea level needs the mass-conservation correction

**Mechanism.** ECCO runs the MITgcm in Boussinesq mode, which conserves
volume rather than mass. A Boussinesq ocean therefore does not represent
global-mean steric (thermosteric) sea level change directly: the
global-mean expansion signal must be added back through the standard
global correction (the Greatbatch adjustment) before the number is used
in a global budget.[^greatbatch-1994]

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
In this bundle the attested steric height computation refuses to pass a
global run whose receipt lacks the Boussinesq caveat field, so no
consumer can quote its global mean as modeled sea surface
rise.[^steric-computation]

**Verification.** The Boussinesq volume-conservation property and the
need for the global steric correction are Greatbatch's result for any
volume-conserving model, which the MITgcm configuration ECCO uses
is;[^greatbatch-1994] the correction changes only the global-mean
scalar, which is checkable by confirming the regional pattern is
unchanged when it is applied.

[^greatbatch-1994]: Greatbatch (1994), J. Geophys. Res. Oceans 99(C6), doi:10.1029/94JC00847
[^steric-computation]: computations/ecco-steric-height.md, the Boussinesq caveat requirement on global runs
