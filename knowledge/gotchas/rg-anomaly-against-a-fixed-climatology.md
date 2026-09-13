---
type: dataset-gotcha
spheres: [hydrosphere]
title: "The Roemmich and Gilson anomalies are departures from the 2004 to 2018 mean and annual cycle, and the extension files keep that reference: joining releases or re-baselining moves an intercept and a comparison, not a slope"
description: "Every anomaly field in the 2019 release and its monthly extensions is defined against the 2004 to 2018 RG climatology, the mean field lives only in the climatology files, and each biennial re-analysis redefines the baseline from more data. Subtracting a different climatology from a single-release series shifts every month by a fixed per-cell, per-calendar-month amount, which moves the intercept and the annual cycle of a fit and leaves a linear slope alone; a series that joins two releases, or a comparison against a product on another baseline, carries the baseline difference as an offset that a trend or a difference plot reads as signal."
tags: [argo, roemmich-gilson, anomaly, baseline, climatology, release, re-baseline, trend, comparison]
generated: { by: knowledge-seeder/claude, at: 2026-09-13T20:20:00Z }
severity: medium
dataset: ../datasets/roemmich-gilson-argo-climatology.md
status: draft
stale_after: 2027-03-13
sources:
  - id: rg-extension-202608
    resource: https://sio-argo.ucsd.edu/RG/RG_ArgoClim_202608_2019.nc.gz
    title: "The August 2026 monthly extension file, downloaded and read with netCDF4 on 2026-09-13: the anomaly variables' long names naming the 2004 to 2018 RG climatology, the absence of a mean field, and the file name's release suffix"
  - id: rg-climatology-temperature
    resource: https://sio-argo.ucsd.edu/RG/RG_ArgoClim_Temperature_2019.nc.gz
    title: "The 2004 to 2018 temperature climatology file; its header, read 2026-09-13, carries the mean field and the 180 monthly anomalies defined by the Jan 2004 to Dec 2018 climatology"
  - id: rg-page
    resource: https://sio-argo.ucsd.edu/RG_Climatology.html
    title: "Scripps RG Argo Climatology product page (read 2026-09-13): the 2019 release's data window, monthly updates between biennial re-analyses, data from 2019 not used in the climatology, and the extension anomaly defined relative to the RG 2019 annual cycle"
  - id: roemmich-gilson-2009
    resource: https://doi.org/10.1016/j.pocean.2009.03.004
    title: "Roemmich and Gilson, 2009, The 2004-2008 mean and annual cycle of temperature, salinity, and steric height in the global ocean from the Argo Program, Progress in Oceanography 82(2), 81-100 (the first release's baseline period, in its title; Crossref registry record verified 2026-09-13, the publisher's page unreachable from the drafting environment)"
  - id: wcrp-2018
    resource: https://doi.org/10.5194/essd-10-1551-2018
    title: "WCRP Global Sea Level Budget Group, 2018, Global sea-level budget 1993-present, Earth System Science Data 10, 1551-1590 (read in full 2026-09-13: section 2.3.3, thermosteric estimates on different baseline climatologies cannot be averaged directly, and the detrend-then-average procedure used instead)"
  - id: dataset
    resource: ../datasets/roemmich-gilson-argo-climatology.md
    title: "This bundle's Roemmich and Gilson dataset concept, which lists the fixed baseline among the known issues"
---

# The Roemmich and Gilson anomalies are departures from a fixed 2004 to 2018 climatology

**Mechanism.** The climatology file holds a mean field and 180
monthly anomalies whose long name reads "defined by Jan 2004 - Dec
2018 (15.0 year) RG CLIMATOLOGY", and every monthly extension file
holds anomaly fields whose long name reads "defined by 2004 - 2018 RG
CLIMATOLOGY" and no mean field at
all.[^rg-climatology-temperature][^rg-extension-202608] The product
page states the same convention in words: the extension anomaly is
defined relative to the RG 2019 annual cycle, and data from 2019
onward are not used in determining the climatology.[^rg-page] The
baseline moves only with a release: major re-analyses are biennial,
the file names carry the release year as a suffix (the 2019 release's
extension files are RG_ArgoClim_YYYYMM_2019.nc.gz), and the first
release described in the 2009 paper was a 2004 to 2008 mean and
annual cycle.[^rg-page][^rg-extension-202608][^roemmich-gilson-2009]
Because the anomaly is the field minus a per-cell mean and annual
cycle, replacing that reference by another subtracts a quantity that
depends on the cell and the calendar month and not on the year: it
shifts the intercept and reshapes the annual cycle of any fit, and
leaves the slope of a linear trend fitted to a single-release series
unchanged. The WCRP assessment records the consequence for
comparison: the thermosteric estimates it compiled are not
necessarily referenced to the same baseline climatology and cannot be
averaged together directly, so the assessment detrended each series,
averaged the variability, averaged the trends separately and
recombined them.[^wcrp-2018]

**Wrong-result mode.** A series that joins anomalies from two
releases (the months of an older release followed by extension files
of the 2019 release, or the 2019 climatology followed by a future
release's extensions) carries a step at the join equal to the
difference of the two baselines at that cell and calendar month; a
trend fitted across the join absorbs the step, and the fit's formal
error does not see it. A difference between this product's anomaly
and another product's anomaly, or between two releases of this
product, reads the baseline difference as an ocean signal. An
"anomaly" from a release used alongside the wrong release's mean
field is an absolute field with a per-cell error equal to the change
in the mean between releases. None of this errors: the files of
different releases share their variable names and grid.

**Correct approach.** A series is built from one release, its
baseline is stated with the number (departure from the 2004 to 2018
RG mean and annual cycle), and an absolute field is the anomaly added
to the mean field of the same release. Across a release change, the
newer release's climatology and extensions replace the older series
in full rather than extend it. A comparison against another product
is made after each series is referred to a common period, or on
detrended variability and trends separately, as the WCRP assessment
did; a trend from a single-release series is unaffected by the choice
of reference period and is quoted with the period it was fitted over.

**Verification.** The long names, the absence of a mean field in the
extension file and the file name convention were read from the
August 2026 extension file with netCDF4 on 2026-09-13; the
climatology file's header, read the same day from the first 4 MB of
the archive, carries the mean field and the anomaly long
name.[^rg-extension-202608][^rg-climatology-temperature] The product
page's statements were read the same day.[^rg-page] The 2009 paper's
baseline period is in its registry title; the Crossref record
(Progress in Oceanography, 2009, volume 82, pages 81 to 100, Roemmich
and Gilson) was verified 2026-09-13, and the publisher's page could
not be fetched from the drafting environment.[^roemmich-gilson-2009]
The WCRP paper was read in full from the publisher's PDF on
2026-09-13.[^wcrp-2018] The dataset concept lists the fixed baseline
among the product's known issues.[^dataset]

[^rg-extension-202608]: RG_ArgoClim_202608_2019.nc.gz, downloaded and read 2026-09-13
[^rg-climatology-temperature]: RG_ArgoClim_Temperature_2019.nc.gz, header read 2026-09-13
[^rg-page]: Scripps RG Argo Climatology product page, read 2026-09-13
[^roemmich-gilson-2009]: Roemmich and Gilson, 2009, Progress in Oceanography, doi:10.1016/j.pocean.2009.03.004 (registry record)
[^wcrp-2018]: WCRP Global Sea Level Budget Group, 2018, Earth System Science Data, doi:10.5194/essd-10-1551-2018
[^dataset]: This bundle's Roemmich and Gilson dataset concept
