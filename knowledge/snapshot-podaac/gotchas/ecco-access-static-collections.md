---
type: dataset-gotcha
title: "ecco_access guesses a dated filename for the static collections; fetch them through CMR"
description: "Given a V4r4 collection with no time dimension (geometry, mixing coefficients) and no date range, ecco_access 0.3.1 synthesized a dated granule filename that the archive answers with a 404 and estimated a 75.8 GB download for a single-granule collection; fetch static collections with earthaccess, whose granule names come from CMR."
tags: [ecco, v4r4, access, ecco_access, earthaccess, geometry, static]
severity: medium
dataset: ../datasets/ecco-v4r4.md
generated: { by: claude-code/fable-5, at: 2026-09-04T19:03:36Z }
status: stable
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
stale_after: 2027-03-04
sources:
  - id: observation-record
    resource: https://github.com/open-science-pillars/ocean-science/blob/14a4eeab071d6f7d10f04e72c4878fef87c8b8de/skills/ecco/references/variable-catalog.md
    title: "The record of the observation (Access pattern section): ecco_access 0.3.1 on 2026-07-04, the synthesized filename, the 404, the 75.8 GB estimate, and the earthaccess workaround"
    author: human:PaulMRamirez
  - id: ecco-access-release
    resource: https://pypi.org/project/ecco-access/0.3.1/
    title: "ecco-access 0.3.1 on PyPI (uploaded 2025-10-29; the latest release on 2026-09-04), source at github.com/ECCO-GROUP/ECCO-ACCESS"
  - id: tut-access-intro
    resource: https://ecco-v4-python-tutorial.readthedocs.io/ECCO_access_intro.html
    title: "ECCO v4 Python Tutorial: The ecco_access library (ecco_podaac_to_xrdataset signature; time_res all includes datasets with no time dimension)"
  - id: tut-grid-params
    resource: https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Loading_the_ECCOv4_native_model_grid_parameters.html
    title: "ECCO v4 Python Tutorial: Loading the ECCOv4 native model grid parameters (the ecco_access route to ECCO_L4_GEOMETRY_LLC0090GRID_V4R4)"
  - id: geometry-family
    resource: ../fields/ecco-v4r4/geometry.md
    title: "The geometry fields concept: the single static granule and its variables"
---

# ecco_access guesses a dated filename for the static collections; fetch them through CMR

**Mechanism.** Two V4r4 collection families have no time dimension,
the grid parameters and the mixing coefficients;[^tut-access-intro] the
native geometry collection (`ECCO_L4_GEOMETRY_LLC0090GRID_V4R4`) is one
granule of about 8.6 MB.[^geometry-family] The tutorial documents the
geometry as loadable through ecco_access like any other collection, and
describes the `time_res='all'` default as including datasets that have
no time dimension.[^tut-access-intro][^tut-grid-params]
Observed 2026-07-04 on ecco_access 0.3.1: asked for the geometry
collection with no date range, the library synthesized a dated granule
filename (`GRID_1992-01-01_...`) that does not exist, the archive
answered 404, and the download estimate came back as 75.8 GB for a
single-granule collection.[^observation-record] 0.3.1 is still the
latest release on PyPI as of 2026-09-04, so the behavior is current,
not historical.[^ecco-access-release]

**Wrong-result mode.** A scripted load that trusts the estimate refuses
or waits on a download that will never arrive; one that trusts the
filename fails with a 404 that reads like an archive outage. Either way
the geometry never merges, and every native-grid analysis downstream
starts without areas, thicknesses, or partial-cell fractions.

**Correct approach.** Fetch the static collections through CMR, where
granule names are listed rather than guessed:
`earthaccess.search_data(short_name=...)` followed by
`earthaccess.download`, then `xarray.open_dataset` on the file and
`xarray.merge` into the data granules.[^observation-record] Keep
ecco_access for the time-ranged collections, with exact ShortNames and
an explicit date range (see the dataset concept). If a later
ecco_access release changes the static-collection behavior, re-observe
before retiring this note; the workaround stays valid regardless,
because it never depends on the library's filename logic.

[^observation-record]: OSP ECCO variable catalog at ocean-science 14a4eea, Access pattern section (observation of 2026-07-04)
[^ecco-access-release]: ecco-access 0.3.1 on PyPI, release listing
[^tut-access-intro]: ECCO v4 Python Tutorial: The ecco_access library
[^tut-grid-params]: ECCO v4 Python Tutorial: Loading the ECCOv4 native model grid parameters
[^geometry-family]: fields/ecco-v4r4/geometry.md
