---
type: dataset
title: SWOT KaRIn Level 2 Low Rate SSH
description: "Wide-swath interferometric SSH, two 50 km swaths with a nadir gap, four product tiers, two version families; baseline recorded here with a verification date."
tags: [swot, karin, ssh, altimetry, podaac]
generated: { by: knowledge-seeder/claude, at: 2026-07-05T00:00:00Z }
resource: https://podaac.jpl.nasa.gov/dataset/SWOT_L2_LR_SSH_D
version: "Version families C (ShortNames *_2.0) and D (*_D) both live in CMR as of 2026-07-04; D is the full-mission reprocessing and the ONLY family carrying the cal/val phase; granule CRIDs observed: PGC0 and PIC0 within C, PGD0 in D (the crid attribute varies within a collection)"
status: stable
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
stale_after: 2027-01-04
sources:
  - id: cmr-sweep
    resource: "https://cmr.earthdata.nasa.gov/search/collections.json?provider=POCLOUD&short_name=SWOT_L2_LR_SSH*&options[short_name][pattern]=true"
    title: "CMR ShortName sweep of 2026-09-04 (SWOT_L2_LR_SSH* and SWOT_L2_NALT*, provider POCLOUD) with a granule holdings probe per collection; public search, no credentials"
  - id: version-d-release-note
    resource: https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/web-misc/swot_mission_docs/SWOT_VersionD_KaRIn_Products_Release_Note_20250423b.pdf
    title: "Release Note: SWOT Version D KaRIn Science Data Products, JPL, 2025-04-23: mission phase timeline, scope of the Version D and C products, CRID meanings"
---

# SWOT KaRIn Level 2 Low Rate SSH

**Identity.** KaRIn wide-swath interferometric altimetry: sea surface
height on two 50 km swaths (2 km posting; 250 m in the Unsmoothed tier)
separated by a ~20 km nadir gap. Four tiers (Basic, Expert, WindWave,
Unsmoothed) plus separate nadir altimeter collections; the inventory
is the Variants section below. Archive: PO.DAAC; launched 2022-12-16;
cal/val 1-day orbit through July 2023, 21-day science orbit
since.[^version-d-release-note]

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

## Variants

All ShortNames below were found in CMR (provider POCLOUD) by the public
sweep of 2026-09-04, exactly once each, with the concept ids and DOIs
CMR reports.[^cmr-sweep] Every KaRIn tier exists in two version
families: `*_2.0` (titled Version C) and `*_D` (Version D). The
umbrella collections `SWOT_L2_LR_SSH_2.0` (C2799438306-POCLOUD, DOI
10.5067/SWOT-SSH-2.0) and `SWOT_L2_LR_SSH_D` (C3233945000-POCLOUD, DOI
10.5067/SWOT-SSH-D) are the parents; the tier collections share the
parent's DOI.

| Tier | Version C ShortName (concept id) | Version D ShortName (concept id) | Contents |
|---|---|---|---|
| Basic | `SWOT_L2_LR_SSH_BASIC_2.0` (C2799465428) | `SWOT_L2_LR_SSH_BASIC_D` (C3233942270) | `ssha_karin` with core flags on the 2 km swath grid |
| Expert | `SWOT_L2_LR_SSH_EXPERT_2.0` (C2799465497) | `SWOT_L2_LR_SSH_EXPERT_D` (C3233942272) | Basic plus the full correction and uncertainty set |
| WindWave | `SWOT_L2_LR_SSH_WINDWAVE_2.0` (C2799465507) | `SWOT_L2_LR_SSH_WINDWAVE_D` (C3233942281) | wind speed and significant wave height |
| Unsmoothed | `SWOT_L2_LR_SSH_UNSMOOTHED_2.0` (C2799465503) | `SWOT_L2_LR_SSH_UNSMOOTHED_D` (C3233942278) | 250 m native posting, no along-track smoothing |

**Family holdings (granule probe of 2026-09-04).**[^cmr-sweep] The
Version C tiers each hold about 20,000 granules running from cycle 001
pass 149 (2023-07-26, CRID PGC0) to cycle 032 (2025-05-03, CRID PIC2)
and return ZERO granules for the calibration window 2023-03-30 to
2023-07-10. The Version D tiers each hold about 33,000 granules from
cycle 473 (2023-03-27, CRID PGD0) through cycle 055 (2026-08-30, CRID
PID0, forward processing), with about 2,780 granules per tier inside
the calibration window. The release note describes Version D as
generated for every measurement from the start of the calibration
phase (2023-03-30) onward and names the last Version C measurements as
2025-04-27,[^version-d-release-note] which the holdings bear out: only
the D family carries the cal/val phase, and only the D family is still
growing. Science-era passes present in both families carry different
CRIDs and product counters (for example `011_424`: `PIC0_01` in C,
`PGD0_02` in D).

**Nadir altimeter.** Conventional altimetry from the nadir instrument
lives in separate collections, three families each with a Version 2.0
and a Version D line: `SWOT_L2_NALT_GDR_2.0` / `SWOT_L2_NALT_GDR_D`
(the geophysical data record with waveforms), `SWOT_L2_NALT_IGDR_2.0`
/ `SWOT_L2_NALT_IGDR_D` (interim) and `SWOT_L2_NALT_OGDR_2.0` /
`SWOT_L2_NALT_OGDR_D` (operational). Each umbrella has sub-collections
`*_GDR_*`, `*_SGDR_*` (GDR and IGDR families only) and `*_SSHA_*` (sea
surface height anomaly), 22 nadir collections in all; DOIs follow the
family (10.5067/SWOT-NALT-GDR-D for the Version D GDR line; the 2.0
IGDR and OGDR lines carry DOIs ending in `-1.0`).[^cmr-sweep]

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
- [swot-crossover-unapplied](../gotchas/swot-crossover-unapplied.md): **Crossover calibration arrives UNAPPLIED in `ssha_karin` /
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

[^cmr-sweep]: CMR ShortName sweep and granule holdings probe of 2026-09-04 (public collections and granules search, provider POCLOUD; the query recorded as this source's resource, run with a Client-Id header and no credentials)
[^version-d-release-note]: Release Note: SWOT Version D KaRIn Science Data Products, JPL, 2025-04-23, Table 2 (orbit and mission phase timeline), section 4 (scope of the Version D and C products), section 3 (CRID meanings); fetched and read 2026-09-04
