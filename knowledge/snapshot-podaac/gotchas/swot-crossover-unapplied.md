---
type: dataset-gotcha
title: "SWOT KaRIn ssha_karin: crossover calibration arrives UNAPPLIED"
description: "Swath or regional ssha statistics computed on ssha_karin without adding height_cor_xover carry a spurious cross-track ramp of order meters."
tags: [swot, karin, ssha, crossover, height-cor-xover, calibration]
generated: { by: knowledge-seeder/claude, at: 2026-07-05T00:00:00Z }
severity: high
dataset: ../datasets/swot-karin.md
eval_case: swot-crossover-unapplied
sources:
  - id: nasa-swot-l2-lr-ssh-d
    resource: https://podaac.jpl.nasa.gov/dataset/SWOT_L2_LR_SSH_D
    title: "PO.DAAC collection page: SWOT_L2_LR_SSH_D (Version D umbrella)"
  - id: pdd-l2-lr-ssh
    resource: https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/web-misc/swot_mission_docs/pdd/D-56407_SWOT_Product_Description_L2_LR_SSH_20250224a_RevC_clean_sig.pdf
    title: "SWOT Product Description, Level 2 KaRIn Low Rate Sea Surface Height Product (L2_LR_SSH), JPL D-56407 Revision C, 2025-02-24: section 4.1.8 KaRIn Corrections"
  - id: version-d-release-note
    resource: https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/web-misc/swot_mission_docs/SWOT_VersionD_KaRIn_Products_Release_Note_20250423b.pdf
    title: "Release Note: SWOT Version D KaRIn Science Data Products, JPL, 2025-04-23: section 7 known issues, crossover correction not applied to reported SSH and SSHA"
status: stable
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
stale_after: 2027-01-04
---

# SWOT KaRIn ssha_karin: crossover calibration arrives UNAPPLIED

**Mechanism.** In the KaRIn Low Rate SSH products the crossover
calibration is NOT pre-applied to `ssha_karin` / `ssh_karin`; the
granule metadata itself instructs adding `height_cor_xover` (gated by
`height_cor_xover_qual`), and the product description says the same:
the correction is not applied in forming `ssh_karin`, `ssh_karin_2`,
`ssha_karin` or `ssha_karin_2`, and its value is to be added by the
user.[^pdd-l2-lr-ssh] The correction addresses a roll/phase
systematic that appears as a cross-track ramp; the release note lists
the unapplied correction among the known product features, with large
cross-track tilts evident in the reported SSH and SSHA unless the user
applies it.[^version-d-release-note]

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
field's mesoscale structure;[^nasa-swot-l2-lr-ssh-d] the swot-karin dataset concept's Known
issues records the observation.

[^nasa-swot-l2-lr-ssh-d]: PO.DAAC collection page: SWOT_L2_LR_SSH_D (Version D umbrella)
[^pdd-l2-lr-ssh]: SWOT Product Description L2_LR_SSH, JPL D-56407 Revision C, 2025-02-24, section 4.1.8 KaRIn Corrections (height_cor_xover "is not applied in forming ssh_karin, ssh_karin_2, ssha_karin, or ssha_karin_2" and "should be added ... by the user if it is to be applied"; height_cor_xover_qual 0 good, 1 suspect, 2 bad); fetched and read 2026-09-04
[^version-d-release-note]: Release Note: SWOT Version D KaRIn Science Data Products, JPL, 2025-04-23, section 7 ("L2_LR_SSH Crossover Correction Not Applied to Reported SSH and SSHA"); fetched and read 2026-09-04
