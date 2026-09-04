---
type: dataset-gotcha
title: "Geostrophic velocity from PHIHYD alone omits the surface pressure: add g times ETAN"
description: "PHIHYD is the hydrostatic pressure anomaly BELOW the free-surface contribution; geostrophic velocity from its gradient alone correlates near zero with the model's currents, and the fix is adding g times ETAN before taking horizontal gradients."
tags: [ecco, geostrophy, pressure, etan, ssh, native-grid]
severity: high
dataset: ../datasets/ecco-v4r4.md
eval_case: ecco-phihyd-surface-pressure
# eval id reserved for the eval-commons seed.
generated: { by: claude-code/fable-5, at: 2026-09-01T05:35:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-01T05:53:24Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: attested-geostrophy
    resource: ../computations/ecco-geostrophic-balance.md
    title: "The attested geostrophic balance computation whose receipts measured both the broken and the fixed forms"
  - id: tutorial-geostrophic
    resource: https://ecco-v4-python-tutorial.readthedocs.io/Geostrophic_balance.html
    title: "ECCO v4 tutorial, geostrophic balance: the reference formulation includes the sea-surface pressure contribution"
---

# PHIHYD alone is not the geostrophic pressure

ECCO's PHIHYD is the hydrostatic pressure potential anomaly BELOW the
free surface: the barotropic loading from sea-surface height is not in
it. A geostrophic velocity computed from gradients of PHIHYD alone is
dimensionally right, spatially smooth, plausible on a map, and wrong,
because at depth the surface pressure gradient is the dominant term of
the balance. The fix is one line: form the full pressure potential as
g times ETAN plus PHIHYD before taking horizontal
gradients.[^tutorial-geostrophic]

This one was caught by our own measurement, not by review. The
attested geostrophic computation's first run (2009-12, 351 m)
correlated at r = -0.04 against the model's own currents; every
reviewer-plausible explanation (tile rotation handedness, staggering
conventions) was tested and refuted by per-tile diagnostics before
the missing term was found. With g times ETAN added the same code
measures r = 0.79 across the 10 to 55 degree band and r = 0.92 in the
open-ocean interior, and those runs are the receipts the attester now
anchors on.[^attested-geostrophy] The lesson the bundle keeps
repeating: a plausible field is not a validated one; correlate against
the model before believing any derived velocity.

[^attested-geostrophy]: computations/ecco-geostrophic-balance.md, the measured broken and fixed runs
[^tutorial-geostrophic]: ECCO v4 tutorial geostrophic balance chapter
