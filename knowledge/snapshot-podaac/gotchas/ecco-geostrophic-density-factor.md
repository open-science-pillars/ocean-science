---
type: dataset-gotcha
title: "Geostrophic velocity from ECCO pressure needs the density factor, not bare PHIHYD gradients"
description: "The hydrostatic pressure anomaly PHIHYD is pressure over reference density; geostrophic velocity is the gradient of rhoConst times PHIHYD divided by in-situ density times f, and dropping the density factor gives plausible but wrong currents."
tags: [ecco, geostrophy, pressure, density, native-grid]
severity: high
dataset: ../datasets/ecco-v4r4.md
eval_case: ecco-geostrophic-density
# eval id reserved for the eval-commons seed.
generated: { by: claude-code/fable-5, at: 2026-09-01T05:11:19Z }
verified: { by: human:PaulMRamirez, at: 2026-09-01T05:53:24Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: ecco-skills-eval
    resource: https://github.com/podaac/ecco-skills/blob/main/docs/eval1.md
    title: "podaac/ecco-skills evaluation round 1: the proposed geostrophic formula omitted density; corrected to dp = rhoConst times grad PHIHYD, then divided by (rhoConst + RHOAnoma) times f"
  - id: tutorial-geostrophic
    resource: https://ecco-v4-python-tutorial.readthedocs.io/Geostrophic_balance.html
    title: "ECCO v4 tutorial, geostrophic balance: the reference geos_vel_compute implementation"
---

# Geostrophic velocity from ECCO pressure needs the density factor

ECCO's PHIHYD is the hydrostatic pressure ANOMALY divided by the
reference density, so a geostrophic velocity computed as one over f
times the gradient of PHIHYD looks dimensionally plausible and is
wrong. The correct chain per the tutorial implementation: recover the
pressure gradient as rhoConst times the PHIHYD gradient, then divide
by the local in-situ density (rhoConst plus RHOAnoma) times f, with
the gradients taken and rotated on the native
grid.[^tutorial-geostrophic]

An independent PO.DAAC skills project proposed the bare-gradient form
in its design; an adversarial evaluation caught the missing density
factor before implementation, and the fixed version reproduces the
tutorial's geos_vel_compute to better than 1e-9 m per s while matching
the model's own interior velocities at correlation
0.998.[^ecco-skills-eval]

[^ecco-skills-eval]: podaac/ecco-skills eval round 1, the caught missing density factor, and its acceptance record
[^tutorial-geostrophic]: ECCO v4 tutorial geostrophic balance chapter
