---
type: dataset-gotcha
spheres: [hydrosphere, geosphere]
title: "A coastal height names its surface: ellipsoidal, orthometric and local datum heights at one site differ by metres to tens of metres"
description: "A GNSS receiver measures heights above an ellipsoid, a tide gauge series is heights above a local datum (the PSMSL RLR datum about 7 m below mean sea level, a CO-OPS tidal datum, or the orthometric geodetic datum NAVD88) and a NASA-SSH grid value is an anomaly against the DTU21 mean sea surface, so the three are heights above three different surfaces. At Brest the RLR datum sits 44.07 to 44.09 m above the GRS80 ellipsoid and the receiver 293 m from the gauge reports a height of 65.834 m, so mean sea level there is about 51 m above the ellipsoid and a GNSS height is not an elevation above the sea. Nothing in an RLR file, a CO-OPS series, a MIDAS table or an SSHA grid carries the surface, and a height joined to a height above another surface is wrong by the separation between them."
tags: [tide-gauge, ellipsoid, orthometric, geoid, datum, navd88, rlr, gnss, altimetry, nasa-ssh, mean-sea-surface, coastal, sea-level, height]
generated: { by: knowledge-seeder/claude, at: 2026-09-15T17:50:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-15T18:32:59Z, role: maintainer, source: https://github.com/open-science-pillars/ocean-science/pull/60 }
severity: high
dataset: ../connectors/psmsl-gauges.md
eval_case: coastal-heights-ellipsoidal-versus-orthometric
status: draft
stale_after: 2027-03-15
sources:
  - id: psmsl-ellipsoid
    resource: https://psmsl.org/data/obtaining/ellipsoid.php
    title: "PSMSL, ellipsoidal links for RLR data (read 2026-09-15): RLR records are heights above a local datum fixed to a benchmark, a GNSS receiver measures heights relative to an ellipsoid, a comparison with altimetry needs the height difference between the tide gauge datum and the reference ellipsoid, the link runs through levelling between the benchmark and the receiver, and all solutions use ITRF2014 and hence GRS80"
  - id: psmsl-rlr-diagram-brest
    resource: https://psmsl.org/data/obtaining/rlr.diagrams/1.php
    title: "PSMSL RLR diagram page for Brest, station 1 (read 2026-09-15): RLR is 12.500 m below primary benchmark NO-47, 2.959 m is added to values from 1846 onwards to refer them to RLR, and the SONEL ellipsoidal information for receiver BRST gives the RLR datum height above the ellipsoid as 44.094 plus or minus 0.007 (ULR7a), 44.078 plus or minus 0.004 (JPL14), 44.073 plus or minus 0.004 (NGL14) and 44.094 plus or minus 0.006 m (GT3) at epoch 2020.0, receiver 293 m from the gauge"
  - id: ngl-brst-station
    resource: https://geodesy.unr.edu/NGLStationPages/stations/BRST.sta
    title: "Nevada Geodetic Laboratory station page for BRST (read 2026-09-15): latitude 48.380, longitude -4.497, height 65.834 m, solutions in IGS20 and the EU plate frame, the note that NGL solutions are in CM with a CM to CF translation file beside the loading predictions, and the nearest stations BRES at 5.43 km and A114 at 5.45 km"
  - id: midas-readme
    resource: https://geodesy.unr.edu/velocities/midas.readme.txt
    title: "The MIDAS velocity file README (read 2026-09-15): columns 25 to 27 are the station's latitude and longitude in degrees and its height in metres, with no surface named for the height"
  - id: blewitt-2004
    resource: https://geodesy.unr.edu/publications/Blewitt_verticals_2004.pdf
    title: "Blewitt, G. (2004), Fundamental ambiguity in the definition of vertical motion, Cahiers du Centre Europeen de Geodynamique et de Seismologie 23, 1 to 4 (read in full 2026-09-15 from the laboratory's site): vertical motion is motion normal to a defined horizontal surface, either an equipotential (the physical model, the classical geoid being the equipotential closest to the mean sea surface and fixed in time) or a conventional ellipsoid (the geometric model, the GPS case, where vertical is normal to a geocentric ellipsoid); relative sea level is the sea surface above the ocean bottom and geocentric sea level is the sea surface against a terrestrial reference frame"
  - id: nasa-ssh-user-guide
    resource: https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/web-misc/nasa-ssh/NASA-SSH_V1_1_UserGuide.pdf
    title: "NASA-SSH V1.1 User Guide, Willis, Fournier, Killett and Marlis, JPL, 17 pages (read 2026-09-15 through the link on the PO.DAAC dataset page; the archive URL redirects to a signed download): every daily and simple grid value is a sea surface height anomaly relative to the DTU21 mean sea surface computed from altimetry over 1993 to 2012, a mean sea surface that accounts for the persistent effects of spatial variations in the static gravitational field, ocean currents, tides, salinity, atmospheric pressure and other long-term oceanographic phenomena; the simple grids are half-degree Gaussian averages of width 100 km over points within 600 km, at most 500 per cell, respecting basin connections, every 7 days from 10 days of passes"
  - id: podaac-nasa-ssh
    resource: https://podaac.jpl.nasa.gov/dataset/NASA_SSH_REF_SIMPLE_GRID_V11
    title: "PO.DAAC dataset page for NASA_SSH_REF_SIMPLE_GRID_V11 (read 2026-09-15): the ssha variable in metres on a 0.5 degree grid, the reference missions from TOPEX/Poseidon through Sentinel-6A, the 10-day grids every 7 days, the basin flags, the DOI 10.5067/NSREF-SG0V11, release date 2026-06-02, and the user guide link"
  - id: nasa-ssh-concept
    resource: https://github.com/open-science-pillars/nasa-daac-knowledge/blob/nasa-daac-knowledge--v2026.9.2/knowledge/podaac/datasets/nasa-ssh.md
    title: "The provider bundle's NASA-SSH dataset concept (knowledge/podaac/datasets/nasa-ssh.md at the nasa-daac-knowledge--v2026.9.2 release tag): the anomaly convention, the known issue that a half-degree cell against the coast carries offshore information because the Gaussian weighting reaches hundreds of kilometres, and the absence of a published uncertainty for the grids"
  - id: coops-datum-gotcha
    resource: coops-datum-and-epoch.md
    title: "This bundle's gotcha on CO-OPS datums: every water level is a height above the datum named in the request, NAVD88 is a geodetic datum that is not mean sea level, the station datum collection carries an orthometric datum, and at Boston the MLLW, MSL and NAVD88 datums sit 3.53, 8.73 and 9.03 ft above the station datum"
  - id: connector
    resource: ../connectors/psmsl-gauges.md
    title: "This bundle's PSMSL connector concept: the RLR datum roughly 7000 mm below mean sea level so that absolute values are meaningless and only differences and trends carry science"
  - id: gnss-connector
    resource: ../connectors/gnss-vertical-velocity.md
    title: "This bundle's GNSS vertical velocity connector concept: the MIDAS table columns the tool reads, the station's height among them, and the frame returned with every answer"
  - id: land-motion-gotcha
    resource: tide-gauge-relative-sea-level-and-land-motion.md
    title: "This bundle's gotcha on relative sea level: the trend comparison between a gauge and altimetry, which the constant datum offsets do not affect and the land motion does"
---

# A coastal height names its surface

**Mechanism.** Vertical position is defined by the horizontal surface
it is measured from, and at a coast three surfaces are in use at once.
A GNSS receiver measures heights relative to an ellipsoid, and in GPS
practice vertical is the normal to a geocentric ellipsoid; the PSMSL
links through SONEL use ITRF2014 and hence GRS80.[^psmsl-ellipsoid][^blewitt-2004]
A tide gauge series is heights above a local datum: the PSMSL RLR
datum is fixed to a benchmark and set roughly 7000 mm below mean sea
level, and a CO-OPS water level is a height above the datum named in
the request, whether a tidal datum such as MLLW or MSL, the station
datum, or NAVD88, a geodetic datum whose heights are orthometric and
which CO-OPS states is not mean sea level.[^psmsl-ellipsoid][^connector][^coops-datum-gotcha]
An orthometric height is the physical class of vertical in Blewitt's
terms, measured from an equipotential surface, the classical geoid
being the equipotential closest to the mean sea surface and fixed in
time.[^blewitt-2004] A NASA-SSH value is neither: every daily and
simple grid value is a sea surface height anomaly in metres relative
to the DTU21 mean sea surface, a surface computed from altimetry over
1993 to 2012 that already accounts for the persistent effects of
spatial variations in the static gravitational field, ocean currents,
tides, salinity and atmospheric pressure, so a value of zero means
the sea surface matched that mean surface and says nothing about a
height above the ellipsoid or above any datum.[^nasa-ssh-user-guide][^podaac-nasa-ssh]
The separations between the surfaces are metres to tens of metres
and are set by the site. At Brest the SONEL solutions place the RLR
datum 44.073 to 44.094 m above the ellipsoid at epoch 2020.0, RLR
lies 12.500 m below the primary benchmark NO-47, and the receiver
BRST, 293 m from the gauge, reports a height of 65.834 m on its
laboratory station page; with the RLR datum about 7 m below mean sea
level, mean sea level at Brest stands about 51 m above the GRS80
ellipsoid, an arithmetic consequence of the cited
numbers.[^psmsl-rlr-diagram-brest][^ngl-brst-station][^connector]
At Boston the CO-OPS datums are 3.53 ft (MLLW), 8.73 ft (MSL) and
9.03 ft (NAVD88) above the station datum, so the orthometric datum
and mean sea level differ by 0.30 ft there and MLLW and NAVD88 by
5.5 ft.[^coops-datum-gotcha] The MIDAS velocity table carries each
station's height in its last column with no surface named, and the
tool that reads it returns the station's frame but not a height
surface; the GNSS connector concept carries the columns.[^midas-readme][^gnss-connector]
A trend comparison between a gauge and altimetry is unaffected by
these constant offsets and affected by the land motion, which is a
separate gotcha.[^land-motion-gotcha]

**Wrong-result mode.** A GNSS height or a MIDAS table height read as
an elevation above the sea puts the Brest receiver 66 m above sea
level when, taking the page's height as ellipsoidal as a
GNSS-derived height is, it stands about 15 m above it, the
difference being the
ellipsoid's separation from the sea surface at that
place.[^ngl-brst-station][^psmsl-rlr-diagram-brest] The mean
difference between an SSHA series and a gauge series read as the
gauge datum's height, or subtracted as a datum correction to put the
two on one axis, is the difference between two arbitrary reference
levels, the DTU21 mean surface over 1993 to 2012 and the RLR datum
or NAVD88, and not a geodetic quantity.[^nasa-ssh-user-guide][^psmsl-ellipsoid]
A gauge level on NAVD88 or on the RLR datum set beside an ellipsoidal
height of the sea surface, or an SSHA taken as a height above the
ellipsoid, differs by the tens of metres between the surfaces, and
the discrepancy is read as a datum error or an altimeter
bias.[^psmsl-ellipsoid][^coops-datum-gotcha] The failure is silent
because every one of these is a number in metres, nothing in an RLR
file, a CO-OPS series, a MIDAS table or an SSHA grid names the
surface, and a benchmark 66 m above the sea on a coast is a plausible
number.[^midas-readme][^nasa-ssh-user-guide][^connector]

**Correct approach.** A coastal height is stated with its surface: the
ellipsoid with its frame and epoch (ITRF2014 and GRS80 for the PSMSL
links, IGS20 for the laboratory's current tables), the geodetic datum
such as NAVD88, the tidal or station datum with its epoch, or the
mean sea surface such as DTU21 with the years it was computed
from.[^psmsl-ellipsoid][^ngl-brst-station][^coops-datum-gotcha][^nasa-ssh-user-guide]
The conversion between two surfaces at a site is a published link,
the RLR datum height above the ellipsoid on the PSMSL RLR diagram
page where an ellipsoidal link exists, or the CO-OPS datum collection
for a station with its orthometric datum, and the uncertainty of the
link travels with it; a series mean difference is not a
link.[^psmsl-rlr-diagram-brest][^coops-datum-gotcha] Where a
comparison needs only trends, the constant offsets fall out and the
land motion remains, with its own gotcha.[^land-motion-gotcha] A
half-degree NASA-SSH cell against a coast carries offshore
information, so its value is not the height of the water at the gauge
even after every surface is reconciled.[^nasa-ssh-concept]

**Verification.** The PSMSL ellipsoidal links page and the Brest RLR
diagram page, the laboratory's BRST station page and MIDAS README,
Blewitt 2004 from the laboratory's site, the PO.DAAC dataset page for
the NASA-SSH simple grids and the NASA-SSH V1.1 User Guide it links
were read on 2026-09-15; the Brest datum heights are as printed on
the RLR diagram page, which attributes them to SONEL, whose site was
not visited, and the receiver height is as printed on the station
page, which names no surface for it.[^psmsl-ellipsoid][^psmsl-rlr-diagram-brest][^ngl-brst-station][^midas-readme][^blewitt-2004][^podaac-nasa-ssh][^nasa-ssh-user-guide]
The CO-OPS datum facts are taken from this bundle's CO-OPS datum
gotcha and were not re-read from the service.[^coops-datum-gotcha]
The 51 m figure, and the receiver's 15 m above mean sea level, are
arithmetic on the RLR datum height, the receiver height and the
connector's 7000 mm convention, not published values. No data were
downloaded and no series was compared.

[^psmsl-ellipsoid]: PSMSL, ellipsoidal links for RLR data, read 2026-09-15
[^psmsl-rlr-diagram-brest]: PSMSL RLR diagram page for Brest (station 1), read 2026-09-15
[^ngl-brst-station]: Nevada Geodetic Laboratory station page for BRST, read 2026-09-15
[^midas-readme]: the MIDAS velocity file README, read 2026-09-15
[^blewitt-2004]: Blewitt, 2004, Fundamental ambiguity in the definition of vertical motion, read 2026-09-15
[^nasa-ssh-user-guide]: NASA-SSH V1.1 User Guide, sections 2, 3 and 5, read 2026-09-15
[^podaac-nasa-ssh]: PO.DAAC dataset page for NASA_SSH_REF_SIMPLE_GRID_V11, read 2026-09-15
[^nasa-ssh-concept]: the provider bundle's NASA-SSH dataset concept at the v2026.9.2 release tag
[^coops-datum-gotcha]: this bundle's CO-OPS datum and epoch gotcha
[^connector]: this bundle's PSMSL connector concept
[^gnss-connector]: this bundle's GNSS vertical velocity connector concept
[^land-motion-gotcha]: this bundle's tide gauge land motion gotcha
