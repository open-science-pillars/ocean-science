---
type: dataset-gotcha
title: "ECCO SSH inverse-barometer variants: pick the convention and never mix them"
description: "ECCO ships several sea-surface-height variables differing by inverse-barometer and reference conventions; mixing them, or mismatching altimetry's IB convention in a comparison, silently shifts trends and attributions."
tags: [ecco, ssh, sea-level, inverse-barometer, altimetry, conventions]
generated: { by: claude-code/opus-4.8, at: 2026-07-05T00:00:00Z }
severity: medium
# medium, not high: the variants are documented product behavior and the
# error bites through convention inconsistency in a comparison or
# decomposition, not through silently wrong single-variable statistics; no
# Phase-1 eval case is specified yet, and steward review sets it if elevated.
dataset: ../datasets/ecco-v4r4.md
sources:
  - id: fields-ssh
    resource: ../fields/ecco-v4r4/ssh.md
    title: "The SSH fields concept: SSH, SSHIBC, SSHNOIBC and ETAN with their conventions, granule-verified 2026-08-30, and the collections' Variants"
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
status: stable
stale_after: 2027-03-04
---

# ECCO SSH inverse-barometer variants: pick the convention and never mix them

**Mechanism.** ECCO v4r4's sea surface height is not a single field. The
family (the [SSH fields concept](../fields/ecco-v4r4/ssh.md) lists
it) differs by inverse-barometer (IB) and reference conventions: `SSH` (IB-corrected, GIA-free model sea
level), `SSHNOIBC` (without the IB correction), `SSHIBC` (the IB
correction field itself), and the model native `ETAN`. They are distinct
quantities, not interchangeable spellings of one variable.[^fields-ssh]

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
concrete variant list is read from the SSH fields concept at analysis
time, since which variants exist is product state, not a fixed rule.

**Verification.** The SSH fields concept enumerates the SSH family with
each variable's convention, granule-verified 2026-08-30;[^fields-ssh]
the convention offset
between `SSH` and `SSHNOIBC` is visible directly by differencing the two
collections for any month.

[^fields-ssh]: fields/ecco-v4r4/ssh.md, the SSH family's variables and Variants
