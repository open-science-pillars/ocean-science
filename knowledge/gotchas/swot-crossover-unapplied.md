---
type: dataset-gotcha
title: "SWOT KaRIn ssha_karin: crossover calibration arrives UNAPPLIED"
description: "Swath or regional ssha statistics computed on ssha_karin without adding height_cor_xover carry a spurious cross-track ramp of order meters."
tags: [swot, karin, ssha, crossover, height-cor-xover, calibration]
timestamp: 2026-07-05
severity: high
dataset: ../datasets/swot-karin.md
eval_case: swot-crossover-unapplied
evidence:
  - https://podaac.jpl.nasa.gov/dataset/SWOT_L2_LR_SSH_D
  - https://github.com/open-science-pillars/ocean-science/blob/main/skills/swot/references/swot-products.md
status: verified
verified: 2026-07-05
verified_by: OSP steward review
---

# SWOT KaRIn ssha_karin: crossover calibration arrives UNAPPLIED

**Mechanism.** In the KaRIn Low Rate SSH products the crossover
calibration is NOT pre-applied to `ssha_karin` / `ssh_karin`; the
granule metadata itself instructs adding `height_cor_xover` (gated by
`height_cor_xover_qual`). The correction addresses a roll/phase
systematic that appears as a cross-track ramp.

**Wrong-result mode (observed 2026-07-05, PGD0 Expert tier, cycle
011).** Flag-gated statistics on the uncorrected `ssha_karin` show a
spurious linear cross-track ramp of order meters (span about +/-2.9 m).
Swath or regional SSH statistics computed without the correction are
silently wrong: quality flags alone do not make them safe. The
corrected field on the same scene showed physically sensible mesoscale
structure (std 0.17 m). Because `ssha_karin` is a plausible, populated
variable, an analysis that averages it "as is" produces a confident
wrong answer.

**Correct approach.** A correct swath or regional statistic adds
`height_cor_xover` (gated by `height_cor_xover_qual`) to `ssha_karin`
before aggregating, and states that the correction was applied. Flag
gating is necessary but not sufficient on its own.

**Verification.** Reproducible on a PGD0 Expert-tier granule (cycle
011, pass 424): the raw field's cross-track ramp versus the corrected
field's mesoscale structure; the swot-karin dataset concept's Known
issues records the observation.
