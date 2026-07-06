---
type: dataset-gotcha
title: "ECCO SSH inverse-barometer variants: pick the convention and never mix them"
description: "ECCO ships several sea-surface-height variables differing by inverse-barometer and reference conventions; mixing them, or mismatching altimetry's IB convention in a comparison, silently shifts trends and attributions."
tags: [ecco, ssh, sea-level, inverse-barometer, altimetry, conventions]
timestamp: 2026-07-05
severity: medium
# medium, not high: the variants are documented product behavior and the
# error bites through convention inconsistency in a comparison or
# decomposition, not through silently wrong single-variable statistics; no
# Phase-1 eval case is specified yet, and steward review sets it if elevated.
dataset: ../datasets/ecco-v4r4.md
evidence:
  - "internal: relocated from ocean-science/skills/sea-level-analysis/SKILL.md during the knowledge-coupling migration, needs a steward evidence link"
status: draft
---

# ECCO SSH inverse-barometer variants: pick the convention and never mix them

**Mechanism.** ECCO v4r4's sea surface height is not a single field. The
family (variable catalog, Variants section) differs by inverse-barometer
(IB) and reference conventions: `SSH` (IB-corrected, GIA-free model sea
level), `SSHNOIBC` (without the IB correction), `SSHIBC` (the IB
correction field itself), and the model native `ETAN`. They are distinct
quantities, not interchangeable spellings of one variable.

**Wrong-result mode.** Two forms: (1) a series, map, or decomposition
assembled from more than one SSH variant folds the convention difference
into the geophysical signal; (2) a comparison against an altimetry
product under a different IB convention attributes the convention offset
to the ocean. Nothing errors; the variants are all valid SSH, so a
careless query returns a self-consistent but mislabeled answer.

**Correct approach.** A sea level analysis chooses one SSH variant to
match the question and states it; a comparison against altimetry picks
the variant matching that altimetry product's IB convention (and says
so); the chosen variant is named in the methods convention block. The
concrete variant list is read from the variable catalog at analysis
time, since which variants exist is product state, not a fixed rule.

**Verification.** The variable catalog's Variants section enumerates the
SSH family and its conventions; this concept was relocated from the
sea-level-analysis skill during the knowledge-coupling migration and
needs a steward evidence link (PO.DAAC SSH collection pages and the ECCO
v4 variable documentation).
