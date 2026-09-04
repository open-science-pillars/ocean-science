---
type: validity-domain
title: "Exclusion: budget claims on interpolated ECCO grids"
description: "Budget and transport claims are excluded on every 0.5 degree interpolated ECCO collection: the native-grid closure property does not survive interpolation."
tags: [validity-domain, ecco, budgets, exclusion]
status: draft
generated: { by: claude-code/fable-5, at: 2026-08-31T03:48:03Z }
stale_after: 2027-02-28
domain:
  products: ["ECCO_L4_*_05DEG_*"]
  claim_classes: [budgets]
  polarity: exclusion
  releases: [V4R4, V4R4B]
sources:
  - id: native-grid-gotcha
    resource: ../gotchas/ecco-native-vs-regridded.md
    title: "ECCO budgets and transports close only on the native llc90 grid (steward-verified, severity high)"
---

# Exclusion: budget claims on interpolated ECCO grids

The first exclusion candidate, and deliberately so: the native-grid
rule is already steward-verified as a high-severity gotcha, so this
domain restates an existing signed fact in the validity-domain shape
rather than asserting anything new.[^native-grid-gotcha] A declaration
of a budgets-class claim on any 0.5 degree interpolated ECCO
collection intersects this exclusion, and the fitness attester answers
OUT, naming this concept in the receipt. Until a steward signs this
domain concept itself, the attester correctly treats it as advisory
only.

[^native-grid-gotcha]: gotchas/ecco-native-vs-regridded.md, the signed native-vs-regridded rule this domain projects into declaration space
