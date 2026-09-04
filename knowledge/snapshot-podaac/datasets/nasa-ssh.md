---
type: dataset
title: "NASA-SSH simple gridded sea surface height anomaly (observational reference)"
description: "The JPL gridded sea surface height anomaly from the reference altimetry missions only (TOPEX/Poseidon and the Jason series), half-degree grids every seven days from ten days of passes, on a fixed mean sea surface with the atmospheric correction applied; the bundle's second observational record, used to confront ECCO's regional sea level."
tags: [altimetry, sea-surface-height, sea-level, nasa-ssh, observations, confrontation]
generated: { by: claude-code/fable-5, at: 2026-09-03T06:10:00Z }
resource: https://doi.org/10.5067/NSREF-SG0V11
version: "V1.1, DOI 10.5067/NSREF-SG0V11, PO.DAAC collection NASA_SSH_REF_SIMPLE_GRID_V11 (C4155232533-POCLOUD); 1315 grids from 1992-10-26 through 2018-01-01 retrieved from the Earthdata archive 2026-09-03 and verified against the archive's checksums; the along-track source is DOI 10.5067/NSREF-AT0V1"
status: draft
stale_after: 2027-03-03
sources:
  - id: user-guide
    resource: https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/web-misc/nasa-ssh/NASA-SSH_V1_1_UserGuide.pdf
    title: "NASA-SSH V1.1 User Guide (PO.DAAC): the gridding, the corrections, the mean sea surface, and what it does and does not say about uncertainty"
  - id: record-note
    resource: ../../../docs/nasa-ssh-record.md
    title: "The record note: the tree on the machine, its manifest, how it was fetched and verified, and what the files say when read live"
  - id: prandi-2021
    resource: https://doi.org/10.1038/s41597-020-00786-7
    title: "Prandi et al. 2021, Local sea level trends, accelerations and uncertainties over 1993-2019, Scientific Data 8, 1: the order of a gridded-altimetry regional trend uncertainty"
  - id: confrontation
    resource: ../computations/ecco-ssh-vs-altimetry.md
    title: "The attested comparison that reads this record against ECCO's regional sea level"
  - id: doctrine
    resource: ../conventions/consistency-versus-confrontation.md
    title: "Why the comparison has to say what the estimate was fitted to"
---

# NASA-SSH simple gridded sea surface height anomaly (observational reference)

**Identity.** NASA-SSH is JPL's sea surface height anomaly product
built from the reference altimetry missions only (TOPEX/Poseidon,
Jason-1, OSTM/Jason-2, Jason-3), one ground track, one set of orbits
and corrections, no interleaved or drifting-orbit missions. The
"simple grid" collection regrids the along-track anomalies to a
half-degree grid: each grid holds ten days of passes centred on the
file's date, a new grid is produced every seven days, and the
gridding is a Gaussian-weighted average that respects basin
boundaries. The anomaly is relative to the DTU21 mean sea surface with
the dynamic atmospheric correction applied, so the inverse-barometer
effect is removed, which is the convention ECCO's `SSH` variable
also follows. The release identifies itself inside every file
(`product_version`, the DOI in `id`, `product_short_name`,
`mean_sea_surface`, `license`), which is where the bundle reads it
from; the licence is Creative Commons Attribution 4.0.[^user-guide]

**Citation the product asks for.** Willis, J. K., S. Fournier, K.
Marlis, E. Killett and J. Sanchez (2026), NASA-SSH: JPL Sea Surface
Height Anomalies, Version 1.1, PO.DAAC, doi:10.5067/NSREF-SG0V11.

**The release on record.** 1315 grids covering 1992-10-26 through
2018-01-01, retrieved through CMR and the authenticated Earthdata
archive, each file verified against the MD5 checksum the archive
publishes beside it, then hashed (SHA-256) into a manifest that reads
the version and DOI from the files and refuses to build if they
disagree. Eight of the grids hold no values anywhere (reference
mission outages), and the comparison that reads the tree records
which. The tree, its manifest, the verification and the terms are in
the record note.[^record-note]

## Uncertainty

The User Guide publishes no uncertainty for the gridded fields. For
the along-track source it states that the orbit error reduction
lowers the RMS variability at crossovers by a variance of about 2.3
cm, and that a pass is removed when its crossover mean exceeds 0.1 m
or its crossover RMS exceeds 0.27 m. A regional trend from a gridded
altimetry product is held, in the published literature, to a local
uncertainty of order 0.8 to 1.2 mm/yr at the 90 percent level over a
similar span (Prandi et al. 2021, for a different multi-mission
product); the bundle cites that order as context and never as this
product's own figure.[^user-guide][^prandi-2021]

## Independence from ECCO

This record is not independent of the ECCO v4r4 estimate in the way
the RAPID array is. The estimate was fitted to along-track sea
surface height from these same missions; NASA-SSH is a reprocessing
of those measurements with its own orbits, corrections and mean sea
surface. A comparison against it shows whether the fit reached a
region at a given scale and what residual it could not remove; it
does not show that the model's sea level is right for reasons the
fit did not supply. The comparison states this in its receipt, and
the convention says why it must.[^confrontation][^doctrine]

## Known issues

- Adjacent grids share passes (ten days of data every seven days),
  so weekly values are not independent samples; the comparison
  averages the grids of a calendar month and lets the month series'
  own autocorrelation set the effective sample size.
- Grids are dated by the centre of their ten-day window, so a grid
  dated the first days of a month carries the last days of the
  previous one; the comparison assigns each grid to the month of its
  centre date and says so.
- Coastal cells carry offshore information: the Gaussian weighting
  reaches hundreds of kilometres, so a half-degree cell against the
  coast is not a coastal measurement.
- Half-degree grids do not resolve the Gulf Stream's meanders or
  shelf processes any better than the model's one-degree class does;
  a box that straddles the Gulf Stream compares two smoothed pictures
  of it.
- A later release (a new version string in the files) is a different
  observation; every comparison names the version it read and is
  re-run, never edited, when the record moves.

[^user-guide]: NASA-SSH V1.1 User Guide, PO.DAAC, sections on the reference missions, the gridding, the corrections and the mean sea surface; fetched and read 2026-09-02
[^record-note]: docs/nasa-ssh-record.md, the record note for release V1.1
[^prandi-2021]: Prandi et al. 2021, Scientific Data 8, 1, doi:10.1038/s41597-020-00786-7, abstract (average local trend uncertainty 0.83 mm/yr, range 0.78 to 1.22, 90 percent confidence, 1993-2019); verified against Crossref 2026-09-02
[^confrontation]: ECCO regional sea level against NASA-SSH altimetry (attested), the comparison and its independence statement
[^doctrine]: Consistency versus confrontation, the convention: independence is a degree, and it is stated
