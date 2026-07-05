---
type: dataset
title: SWOT KaRIn Level 2 Low Rate SSH
description: "Wide-swath interferometric SSH, two 50 km swaths with a nadir gap, four product tiers, two version families; baseline recorded here with a verification date."
tags: [swot, karin, ssh, altimetry, podaac]
timestamp: 2026-07-05
resource: https://podaac.jpl.nasa.gov/dataset/SWOT_L2_LR_SSH_D
version: "Version families C (ShortNames *_2.0) and D (*_D) both live in CMR as of 2026-07-04; D is the full-mission reprocessing and the ONLY family carrying the cal/val phase; granule CRIDs observed: PGC0 and PIC0 within C, PGD0 in D (the crid attribute varies within a collection)"
status: verified
verified: 2026-07-05
verified_by: OSP steward review
---

# SWOT KaRIn Level 2 Low Rate SSH

**Identity.** KaRIn wide-swath interferometric altimetry: sea surface
height on two 50 km swaths (2 km posting; 250 m in the Unsmoothed tier)
separated by a ~20 km nadir gap. Four tiers (Basic, Expert, WindWave,
Unsmoothed) plus separate nadir altimeter collections; inventory and
granule anatomy in the plugin's swot-products reference. Archive:
PO.DAAC; launched 2022-12-16; cal/val 1-day orbit through July 2023,
21-day science orbit since.

**Structure (granule-verified 2026-07-04, Basic tier, D family).** One
granule per pass, dims `(num_lines, num_pixels, num_sides)` observed as
9866 x 69 x 2; key variables: `ssha_karin` with `ssha_karin_qual`,
`ssh_karin` with `ssh_karin_qual` and `ssh_karin_uncert`, alternate
processing pair `ssha_karin_2`/`ssh_karin_2`, ancillary fields
including `geoid`, `mean_sea_surface_cnescls` (with `_uncert`),
`internal_tide_hret`, `distance_to_coast`, and categorical flags
(`ancillary_surface_classification_flag`, `dynamic_ice_flag`,
`rain_flag`, `rad_surface_type_flag`). The processing baseline is the
global attribute `crid`. A 3-day Gulf Stream regional query returned 8
granules at about 9.4 MB each; a loaded open-ocean pass had 39% valid
`ssha_karin` after flag and land gating, so masked fractions of this
order are normal, not a defect.

## Uncertainty

- `ssh_karin_uncert` (Basic) estimates per-sample RANDOM noise
  (1-sigma); it does not include the correlated swath-scale systematic
  errors (roll, phase, timing, wet troposphere residuals) that
  dominate at long cross-track wavelengths. Treating `*_uncert` as the
  total error budget understates uncertainty on any swath-scale
  average.
- The Expert tier exposes the crossover-calibration corrections
  (`height_cor_xover` appears already in Basic with its qual flag) and
  the full correction stack for custom error handling.
- `mean_sea_surface_cnescls_uncert` covers the reference surface, which
  matters for absolute SSH but cancels in ssha time differences.
- Quality flags are categorical gates, not quantitative uncertainty
  (core QC rule); the 39% valid fraction above illustrates their bite.

## Known issues

- [swot-calval-orbit-phases](../gotchas/swot-calval-orbit-phases.md):
  orbit phases and the version-family trap.
- Baseline drift within collections: CRIDs change as forward
  processing and reprocessing interleave; the `crid` attributes of the
  granules actually loaded are the only record of which baseline a
  subset came from, so consistency claims depend on their being
  captured at load time.
- **Crossover calibration arrives UNAPPLIED in `ssha_karin` /
  `ssh_karin`** (observed 2026-07-05 on PGD0 Expert-tier granules,
  cycle 011): flag-gated statistics on the uncorrected field show a
  spurious linear cross-track ramp of order meters (a roll/phase
  systematic), and the granule metadata itself instructs adding
  `height_cor_xover` (gated by `height_cor_xover_qual`). Swath or
  regional statistics computed without that correction are silently
  wrong; the corrected field on the same scene showed physically
  sensible mesoscale structure (std 0.17 m vs the raw ramp's +/-2.9 m
  span). Ingested from the Tutorial 2 fresh walkthrough.
- CMR spatial search matches whole pole-to-pole passes; a matched pass
  can carry zero in-box pixels, so regional statistics subset to the
  region before any aggregation (observed on pass 011/424, same
  walkthrough).
