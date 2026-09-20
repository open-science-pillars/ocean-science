---
type: recipe
spheres: [hydrosphere, geosphere]
title: "Regional sea level trend at a coast: the altimetry trend, the GIA model, the land motion at the gauge and the tide gauge relative trend reconciled"
description: "How a coastal sea level trend is assembled from four numbers that are not the same quantity: the NASA-SSH altimetry trend in a box against the coast (geocentric, an anomaly against the DTU21 mean sea surface, with offshore information in the coastal cells), the GIA correction named by its model (the PSMSL Peltier set, ICE-5G v1.3 with VM2 and a 90 km lithosphere, one rate for the gauge and one for the GNSS receiver), the vertical land motion at the gauge from gnss_vertical_velocity with its frame and uncertainty, and the PSMSL RLR relative trend over the same window. The identity is geocentric trend equals relative trend plus land uplift; the residual against the altimetry is read against the combined uncertainty and the two differences of place before any altimeter bias."
tags: [sea-level, trend, coastal, regional, altimetry, nasa-ssh, tide-gauge, psmsl, gia, vertical-land-motion, gnss, midas, recipe]
generated: { by: knowledge-seeder/claude, at: 2026-09-15T17:50:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-15T18:32:59Z, role: maintainer, source: https://github.com/open-science-pillars/ocean-science/pull/60 }
status: stable
stale_after: 2027-03-15
inputs:
  - altimetry: "the NASA-SSH V1.1 simple grids (the provider bundle's dataset concept, cited below): monthly means of the half-degree ssha grids over the box the reader names against the coast, each grid a Gaussian average of width 100 km over points within 600 km, ten days of passes every seven days, anomalies against the DTU21 mean sea surface"
  - gauge: ../connectors/psmsl-gauges.md
  - land_motion: ../connectors/gnss-vertical-velocity.md
  - gia: "the PSMSL Peltier set, ICE-5G v1.3 with the VM2 Earth model and a 90 km lithosphere, supplied 2012: the relative sea level rate at the PSMSL station (the tide gauge quantity) and the crustal uplift rate (the GNSS quantity), the variant centred on now"
  - method: "the method this package's attested trend computation fixes (the ecco-trend-ci computation, cited below), re-implemented on the altimetry month series and on the gauge month series over one window: the monthly climatology fitted jointly with the slope, an ordinary least squares slope against time in months, the lag-1 autocorrelation r1 of the residuals, an effective sample size n (1 - r1) / (1 + r1) capped at n, and a two-sided 95 percent interval from Student's t on n_eff minus 2 degrees of freedom; the attested executor accepts only series that arrive inside a sanctioned receipt whose data record is a verified-tree stamp, psmsl_monthly produces no receipt and the only sanctioned producer of a NASA-SSH box series needs an ECCO partition receipt as its other side, so each trend here is a trend by the sanctioned method and not an attested trend, until a computation that reads a gauge series and a NASA-SSH box series into a receipt exists"
expected:
  - quantity: "the identity"
    statement: "the geocentric sea level trend at the gauge is the relative trend plus the up velocity of the land, positive up meaning the land rises; the altimetry trend in the box less that sum is the residual of the reconciliation, and it is read against the combined uncertainty and against the two known differences of place, the offshore information in a coastal altimetry cell and the distance from the receiver to the gauge, before it is read as an altimeter bias"
  - quantity: "worked land motion term, Brest"
    statement: "the four SONEL solutions on receiver BRST, 293 m from the gauge, over 1998-10-31 to 2023-03-23 in ITRF2014, whose rates and uncertainties this bundle's land motion gotcha carries (cited below), spread over 1.28 mm per year; the laboratory's tide gauge estimate for Brest is -1.136 mm per year with a formal uncertainty of 0.269, spatial variability 0.443 and temporal variability 0.996 mm per year, from five stations at 0.29 to 31.25 km, rated good, in the IGS14 frame; the term a reconciliation at Brest carries is the chosen solution's rate with that 1.28 mm per year spread reported beside it, or the laboratory's estimate with its four parameters"
  - quantity: "the GIA term"
    statement: "a model value with no error bar: the PSMSL set gives at each station one relative sea level rate for the gauge and one crustal uplift rate for the GNSS receiver, from ICE-5G v1.3 with VM2 and a 90 km lithosphere, in three variants of which the centred one is recommended and whose spread is stated not to be an error bar; another model gives another value, and the uncorrected trend stands beside the corrected one"
expected_uncertainty:
  - quantity: "altimetry trend"
    statement: "the product publishes no uncertainty for the grids; the interval is the sampling interval from the month series' own autocorrelation under the sanctioned method as re-implemented here, not an attested interval, and the published order of a regional gridded-altimetry trend uncertainty, 0.8 to 1.2 mm per year at the 90 percent level over 1993 to 2019 for a different product, is context and never this product's figure"
  - quantity: "gauge trend"
    statement: "the interval from the same re-implemented method over the same window, not an attested interval, with the record's span and gaps stated; CO-OPS's published widths of about plus or minus 1.5 mm per year at 30 years and plus or minus 0.5 mm per year at 60 years give the order"
  - quantity: "land motion"
    statement: "the larger of the chosen solution's own uncertainty and the spread across the solutions on the receiver, 1.28 mm per year at Brest, or the laboratory's four uncertainty parameters where its tide gauge estimate is used; the frame stated and the same on both sides of any difference"
  - quantity: "combined"
    statement: "the three observed terms combined in quadrature; the GIA model named beside them and never folded into the observed uncertainty; a residual inside the combined interval is closure, a residual outside it is first read against the coastal cell's offshore reach and the receiver's distance from the gauge"
sources:
  - id: nasa-ssh-concept
    resource: https://github.com/open-science-pillars/nasa-daac-knowledge/blob/nasa-daac-knowledge--v2026.9.2/knowledge/podaac/datasets/nasa-ssh.md
    title: "The provider bundle's NASA-SSH dataset concept (knowledge/podaac/datasets/nasa-ssh.md at the nasa-daac-knowledge--v2026.9.2 release tag): the reference missions, the DTU21 anomaly convention, the coastal cells carrying offshore information, the overlapping weekly grids, the absence of a published grid uncertainty and the published order of a regional altimetry trend uncertainty from Prandi and others 2021"
  - id: podaac-nasa-ssh
    resource: https://podaac.jpl.nasa.gov/dataset/NASA_SSH_REF_SIMPLE_GRID_V11
    title: "PO.DAAC dataset page for NASA_SSH_REF_SIMPLE_GRID_V11 (read 2026-09-15): the ssha variable in metres on a 0.5 degree grid, the 10-day grids every 7 days, the basin flags, the reference missions through Sentinel-6A, the DOI 10.5067/NSREF-SG0V11 and the user guide link"
  - id: nasa-ssh-user-guide
    resource: https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/web-misc/nasa-ssh/NASA-SSH_V1_1_UserGuide.pdf
    title: "NASA-SSH V1.1 User Guide, Willis, Fournier, Killett and Marlis, JPL (read 2026-09-15 through the PO.DAAC dataset page's link): the simple grids as Gaussian averages of width 100 km over at most 500 points within 600 km respecting basin connections, every 7 days from 10 days of passes so that adjacent grids share data, anomalies relative to the DTU21 mean sea surface computed from altimetry over 1993 to 2012, and a consistent reference frame for the orbits among the homogenisation steps"
  - id: trend-method
    resource: ../computations/ecco-trend-ci.md
    title: "This package's attested trend computation (knowledge/computations/ecco-trend-ci.md): the one sanctioned linear trend with an interval from a monthly series' own autocorrelation, whose executor accepts only series that arrive inside a sanctioned receipt with a verified-tree stamp, so that a trend over a series of unknown origin is not attested whatever its arithmetic. It was in the provider bundle before it moved here, at https://github.com/open-science-pillars/nasa-daac-knowledge/blob/nasa-daac-knowledge--v2026.9.2/knowledge/podaac/computations/ecco-trend-ci.md on the nasa-daac-knowledge--v2026.9.2 release tag"
  - id: psmsl-ellipsoid
    resource: https://psmsl.org/data/obtaining/ellipsoid.php
    title: "PSMSL, ellipsoidal links for RLR data (read 2026-09-15): RLR records as relative mean sea level against the local land, the land movement removed for a reconstruction and the datum height above the ellipsoid needed for a comparison with altimetry, the link through levelling to a nearby GNSS receiver, the solution, height, rate, epoch, span and distance published per link, positive rates meaning the land rises, and ITRF2014 with GRS80 for every solution"
  - id: psmsl-rlr-diagram-brest
    resource: https://psmsl.org/data/obtaining/rlr.diagrams/1.php
    title: "PSMSL RLR diagram page for Brest, station 1 (read 2026-09-15): the four SONEL solutions on BRST with their vertical rates, uncertainties, datum heights, epoch 2020.0, span 1998-10-31 to 2023-03-23 and distance 293 m"
  - id: psmsl-gia
    resource: https://psmsl.org/train_and_info/geo_signals/gia/
    title: "PSMSL, glacial isostatic adjustment (read 2026-09-15): near the former loads the crust rises and relative sea level falls, around them the forebulge collapses and relative sea level rises, and GIA also changes the sea surface, so a correction for crustal motion alone removes only part of it; ICE-5G (VM2) and ICE-5G (VM4) predictions and other models available"
  - id: psmsl-peltier
    resource: https://psmsl.org/train_and_info/geo_signals/gia/peltier/
    title: "PSMSL, Peltier GIA data sets (read 2026-09-15): files from Drummond and Peltier of 13 August 2012, ICE-5G v1.3 with VM2 and a 90 km lithosphere, one table of relative sea level rates (the tide gauge prediction) and one of crustal uplift rates (the GPS or GNSS prediction) at the PSMSL stations plus one degree grids, three rate variants of which the centred one is recommended and whose spread is definitely not an error bar, spherical harmonics to degree 256"
  - id: peltier-2004
    resource: https://doi.org/10.1146/annurev.earth.32.082503.144359
    title: "Peltier, W. R. (2004), Global glacial isostasy and the surface of the ice-age Earth: the ICE-5G (VM2) model and GRACE, Annual Review of Earth and Planetary Sciences 32, 111 to 149 (Crossref record and abstract read 2026-09-15: title, author, journal, volume, pages and year confirmed; the publisher's page was not fetched)"
  - id: ngl-vlm
    resource: https://geodesy.unr.edu/vlm.php
    title: "The laboratory's vertical land motion at PSMSL tide gauges page (read 2026-09-15): a record for every PSMSL gauge with the imaged rate, its formal uncertainty, the median spatial structure function value, the spatial and temporal variabilities, the contributing stations with their MIDAS rates, uncertainties, distances and weights, and a good, medium or poor rating; Brest rated good at -1.136 mm per year with 0.269, 0.990, 0.443 and 0.996 as its parameters, from A114, BGBC, BRES, BRST and PNDB at 5.69, 10.92, 5.14, 0.29 and 31.25 km; the MIDAS rates linked as the IGS14 table"
  - id: hammond-2021
    resource: https://geodesy.unr.edu/publications/HammondEtAl2021.pdf
    title: "Hammond, W. C., G. Blewitt, C. Kreemer and R. S. Nerem (2021), GPS Imaging of global vertical land motion for studies of sea level rise, Journal of Geophysical Research: Solid Earth 126, e2021JB022355, doi:10.1029/2021JB022355 (read 2026-09-15 from the laboratory's site: the abstract, the introduction, the data and GPS Imaging method sections, the uncertainty parameters, the tide gauge rating criteria and the discussion): rates at over 2,300 PSMSL gauges from a weighted median of the filtered MIDAS rates of the connected stations, solutions aligned to the IGS14 realisation of ITRF2014, four uncertainty parameters per gauge (the rate uncertainty, the structure function value at the nearest station's distance, the nearest neighbour spatial variability and the temporal rate variability), the good rating as no parameter in the worst tercile (33.1 percent of gauges), poor as any parameter in the worst 5 percent (15.5 percent), medium the rest; connecting open ocean altimetry to the coast is stated to be challenging"
  - id: crossref-hammond
    resource: https://api.crossref.org/works/10.1029/2021JB022355
    title: "Crossref record read 2026-09-15: GPS Imaging of Global Vertical Land Motion for Studies of Sea Level Rise, Hammond, Blewitt, Kreemer and Nerem, Journal of Geophysical Research: Solid Earth, volume 126, issue 7, 2021"
  - id: crossref-eos
    resource: https://api.crossref.org/works/10.1029/2018EO104623
    title: "Crossref record read 2026-09-15: Harnessing the GPS Data Explosion for Interdisciplinary Science, Blewitt, Hammond and Kreemer, Eos, volume 99, 2018, the citation the laboratory asks for on its data products"
  - id: gnss-connector
    resource: ../connectors/gnss-vertical-velocity.md
    title: "This bundle's GNSS vertical velocity connector concept: gnss_vertical_velocity by station id or by the three nearest stations to a point with their distances, the up velocity and uncertainty in mm per year, the frame, epochs and steps returned with every answer, the IGS20 table read once per process"
  - id: psmsl-connector
    resource: ../connectors/psmsl-gauges.md
    title: "This bundle's PSMSL connector concept: psmsl_monthly on the RLR path, the sentinel dropped and counted"
  - id: coops-connector
    resource: ../connectors/coops-tides.md
    title: "This bundle's CO-OPS connector concept, the other gauge source, served on a declared datum"
  - id: land-motion-gotcha
    resource: ../gotchas/tide-gauge-relative-sea-level-and-land-motion.md
    title: "This bundle's gotcha: a tide gauge trend is relative sea level and carries the land's vertical motion"
  - id: gia-gotcha
    resource: ../gotchas/tide-gauge-gia-is-modelled.md
    title: "This bundle's gotcha: the GIA correction is a model prediction that names its ice and Earth model and which of its two rates was applied"
  - id: record-length-gotcha
    resource: ../gotchas/tide-gauge-record-length-and-gaps.md
    title: "This bundle's gotcha: a gauge trend carries its record length, its gaps and a confidence interval, with the CO-OPS widths"
  - id: rlr-gotcha
    resource: ../gotchas/psmsl-rlr-versus-metric.md
    title: "This bundle's gotcha: the RLR series and not the metric one carries a trend"
  - id: coops-datum-gotcha
    resource: ../gotchas/coops-datum-and-epoch.md
    title: "This bundle's gotcha: a CO-OPS water level is a height above the datum named in the request, on the 1983 to 2001 epoch"
  - id: heights-gotcha
    resource: ../gotchas/coastal-heights-ellipsoidal-versus-orthometric.md
    title: "This bundle's gotcha: a coastal height names its surface, and levels above different surfaces are not compared"
  - id: frame-gotcha
    resource: ../gotchas/velocity-reference-frame.md
    title: "This bundle's gotcha: a vertical velocity carries its reference frame, and a difference is taken within one frame"
---

# Regional sea level trend at a coast

The quantity a coast asks for is how fast the sea rises against the
land, and the four records that bear on it measure four different
things: altimetry measures the sea surface against a geocentric frame,
a tide gauge measures it against a benchmark on the local land, a
GNSS receiver measures the land against the ellipsoid, and a GIA
model predicts a part of both the land's and the sea surface's
motion.[^psmsl-ellipsoid][^psmsl-gia][^land-motion-gotcha] The recipe
puts them on one footing as trends over one window, and its check is
an identity with a residual.

**Step 1, the altimetry trend near the coast.** The NASA-SSH simple
grids give a sea surface height anomaly on a half-degree grid, an
anomaly against the DTU21 mean sea surface, each grid a Gaussian
average of width 100 km over the passes within 600 km during ten
days, every seven days, so that adjacent grids share
data.[^nasa-ssh-user-guide][^podaac-nasa-ssh] The reader names a box
against the coast, averages the grids of each calendar month, and
fits a trend over a stated window by the method this package's
attested computation fixes, re-implemented here: the climatology
fitted jointly with the slope, ordinary least squares, the lag-1
autocorrelation of the residuals, an effective sample size capped at
the sample, and a two-sided 95 percent interval from Student's t on
the effective degrees of freedom less two.[^trend-method] The attested
executor accepts only series that arrive inside a sanctioned receipt
whose data record is a verified-tree stamp, and the only sanctioned
producer of a NASA-SSH box month series needs an ECCO partition
receipt as its other side, so this trend is a trend by the
sanctioned method and not an attested one until a computation that
reads a NASA-SSH box series into a receipt exists.[^trend-method]
The provider's verified record ends 2018-01-01; a window past it
needs a new stamped record.[^nasa-ssh-concept]
Two facts travel with the number: the product publishes no
uncertainty for its grids, and a cell against the coast carries
offshore information because the weighting reaches hundreds of
kilometres, so the trend is the box's and not the gauge's, and
Hammond and others state that connecting open ocean altimetry to the
coast is itself a challenge.[^nasa-ssh-concept][^hammond-2021] The
anomaly is a height above no datum, and the recipe compares trends
and anomalies only, never levels.[^heights-gotcha]

**Step 2, the GIA correction named with its model.** GIA moves the
crust and the sea surface: relative sea level falls where the crust
still rises near the former loads and rises where the forebulge
collapses, and a correction for crustal motion alone removes only
part of the effect.[^psmsl-gia] The set PSMSL distributes is ICE-5G
v1.3 with the VM2 Earth model and a 90 km lithosphere, supplied in
2012, as one table of relative sea level rates at the PSMSL stations
(the tide gauge quantity) and one of crustal uplift rates (the GNSS
quantity), each in three variants of which the centred one is
recommended and whose spread is stated not to be an error
bar.[^psmsl-peltier][^peltier-2004] A GIA-corrected relative trend
applies the relative sea level rate to the gauge; a GIA-corrected land
motion applies the crustal uplift rate to the GNSS velocity; the
model, its version and which rate was applied are named, the
uncorrected number stands beside the corrected one, and another model
gives another value.[^gia-gotcha] Relative sea level is the sea
surface less the crust, the definition the identity in step 5 uses,
so the model's sea surface rate at a station, the part of GIA an
altimetry trend carries, is the relative sea level rate plus the
crustal uplift rate, both of which the set carries: a derived model
value with no uncertainty of its own.[^psmsl-peltier][^psmsl-gia]
The recipe's identity is stated on uncorrected quantities, and a
GIA-corrected version applies one named model to every term on both
sides, the sea surface rate to the altimetry, the relative sea level
rate to the gauge and the crustal uplift rate to the
velocity.[^psmsl-peltier][^gia-gotcha]

**Step 3, the land motion at the gauge.** The tool returns a station's
up velocity, its uncertainty, the frame, the epochs and the steps
assumed, by the four-character id of the receiver the PSMSL station
page names where an ellipsoidal link exists, or by the three nearest
stations to the gauge's coordinates with their distances; the
laboratory asks that its Eos paper be cited for the
products.[^gnss-connector][^crossref-eos] Where PSMSL prints an
ellipsoidal link, the RLR diagram page carries the SONEL solutions
on the same receiver in ITRF2014, with the rate, its uncertainty, the
span and the distance to the gauge; at Brest the four solutions on
BRST, whose rates the land motion gotcha carries, span 1.28 mm per
year, more than any one solution's stated
uncertainty.[^psmsl-ellipsoid][^psmsl-rlr-diagram-brest][^land-motion-gotcha]
The laboratory's own tide gauge table gives a rate imaged to the gauge
from the connected stations by a weighted median, with four
uncertainty parameters and a good, medium or poor rating; at Brest
it is -1.136 mm per year, formal uncertainty 0.269, spatial
variability 0.443 and temporal variability 0.996, from five stations
at 0.29 to 31.25 km, rated good, in the IGS14 frame the page
links.[^ngl-vlm][^hammond-2021][^crossref-hammond] The velocity
carries its frame, IGS20 from the tool's current table, IGS14 from
the laboratory's tide gauge table, ITRF2014 from SONEL, and a
difference between two velocities is taken within one
frame.[^frame-gotcha] The land motion term is the chosen solution's
rate with the larger of its own uncertainty and the spread across the
solutions on the receiver, or the laboratory's estimate with its four
parameters, and the distance from the receiver to the gauge is stated
with it.[^psmsl-rlr-diagram-brest][^ngl-vlm]

**Step 4, the tide gauge relative trend.** The gauge series is the
PSMSL RLR monthly series through psmsl_monthly, on the RLR path and
not the metric one, with the sentinel dropped and the months dropped
counted, or a CO-OPS station series on a declared datum for a United
States gauge; its trend is fitted by the same re-implemented method
over the same window as the altimetry, unattested because
psmsl_monthly produces no receipt, and it is stated with the record's
span, its gaps and its interval, CO-OPS's practice of a 30-year
minimum and its published widths giving the
order.[^psmsl-connector][^rlr-gotcha][^coops-connector][^coops-datum-gotcha][^record-length-gotcha][^trend-method]
The number is relative sea level: the sum of sea surface change and
vertical land motion at the gauge.[^land-motion-gotcha]

**Step 5, the reconciliation.** With positive up meaning the land
rises, as PSMSL defines it, the geocentric trend at the gauge is the
relative trend plus the up velocity, and the residual is the altimetry
trend in the box less that sum.[^psmsl-ellipsoid][^land-motion-gotcha]
The combined uncertainty is the three observed intervals in
quadrature, the altimetry's and the gauge's from the re-implemented
method's intervals, the land motion's as stated in step 3, with the
GIA model named beside them and never folded in; the two trends and
the residual are stated as results by the sanctioned method and not
as attested results.[^trend-method][^record-length-gotcha][^gia-gotcha]
A residual inside the combined interval closes the reconciliation. A
residual outside it is read first against the two known differences
of place, the coastal cell's offshore reach and the receiver's
distance from the gauge, and then against the choice of solution,
before it is read as an altimeter bias or a coastal
signal.[^nasa-ssh-concept][^hammond-2021][^psmsl-rlr-diagram-brest]

**The checks a reader runs.** The two series cover the same months
and the gauge's gaps are counted, not interpolated.[^record-length-gotcha]
The gauge series is RLR, not metric.[^rlr-gotcha] Every velocity in
the reconciliation carries the same frame and the tool's answer names
it.[^frame-gotcha][^gnss-connector] A rising land (positive up)
puts the relative trend below the geocentric one; the opposite sign
means the velocity's convention was misread.[^psmsl-ellipsoid] No
level is compared, only trends and anomalies, so no datum height or
ellipsoidal height enters.[^heights-gotcha] The GIA model is named
with its version, the rate applied to each quantity is the right one
of the two, and the uncorrected numbers stand beside.[^gia-gotcha][^psmsl-peltier]
The residual is quoted with the combined interval and the two
differences of place stated.[^nasa-ssh-concept][^ngl-vlm] Both
trends are stated as trends by the sanctioned method, re-implemented,
and not as attested trends, since neither series arrives in a
sanctioned receipt.[^trend-method]

**Verification.** The PO.DAAC dataset page and the NASA-SSH V1.1 User
Guide, PSMSL's ellipsoidal links page, Brest RLR diagram page, GIA
page and Peltier GIA data sets page, the laboratory's vertical land
motion page and Hammond and others 2021 from its site were read on
2026-09-15; the Crossref records of Hammond and others 2021, Blewitt
and others 2018 and Peltier 2004 were verified the same
day.[^podaac-nasa-ssh][^nasa-ssh-user-guide][^psmsl-ellipsoid][^psmsl-rlr-diagram-brest][^psmsl-gia][^psmsl-peltier][^ngl-vlm][^hammond-2021][^crossref-hammond][^crossref-eos][^peltier-2004]
No grid, series, velocity table or model file was downloaded and no
trend was computed; the Brest numbers are as printed on the two pages
that carry them, and no reconciled trend is quoted for any site.

[^nasa-ssh-concept]: the provider bundle's NASA-SSH dataset concept at the v2026.9.2 release tag
[^podaac-nasa-ssh]: PO.DAAC dataset page for NASA_SSH_REF_SIMPLE_GRID_V11, read 2026-09-15
[^nasa-ssh-user-guide]: NASA-SSH V1.1 User Guide, sections 3 and 5, read 2026-09-15
[^trend-method]: computations/ecco-trend-ci.md, this package's attested trend computation
[^psmsl-ellipsoid]: PSMSL, ellipsoidal links for RLR data, read 2026-09-15
[^psmsl-rlr-diagram-brest]: PSMSL RLR diagram page for Brest (station 1), read 2026-09-15
[^psmsl-gia]: PSMSL, glacial isostatic adjustment page, read 2026-09-15
[^psmsl-peltier]: PSMSL, Peltier GIA data sets page, read 2026-09-15
[^peltier-2004]: Peltier, 2004, Annual Review of Earth and Planetary Sciences 32, doi:10.1146/annurev.earth.32.082503.144359, Crossref record and abstract read 2026-09-15
[^ngl-vlm]: the laboratory's vertical land motion at tide gauges page, read 2026-09-15
[^hammond-2021]: Hammond and others, 2021, Journal of Geophysical Research: Solid Earth 126, doi:10.1029/2021JB022355, read 2026-09-15
[^crossref-hammond]: Crossref record of Hammond and others 2021, read 2026-09-15
[^crossref-eos]: Crossref record of Blewitt, Hammond and Kreemer 2018, read 2026-09-15
[^gnss-connector]: this bundle's GNSS vertical velocity connector concept
[^psmsl-connector]: this bundle's PSMSL connector concept
[^coops-connector]: this bundle's CO-OPS connector concept
[^land-motion-gotcha]: this bundle's tide gauge land motion gotcha
[^gia-gotcha]: this bundle's modelled GIA correction gotcha
[^record-length-gotcha]: this bundle's record length and gaps gotcha
[^rlr-gotcha]: this bundle's RLR versus metric gotcha
[^coops-datum-gotcha]: this bundle's CO-OPS datum and epoch gotcha
[^heights-gotcha]: this bundle's coastal heights gotcha
[^frame-gotcha]: this bundle's velocity reference frame gotcha
