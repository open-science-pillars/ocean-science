---
type: dataset-gotcha
spheres: [geosphere, hydrosphere]
title: "A vertical velocity carries its reference frame: the IGS20, IGS14, ITRF2014 and plate-fixed rates of one station are different numbers"
description: "Vertical motion is defined by the reference frame it is measured in, and the frame is realised by a set of station coordinates, an origin convention and a scale, so two analyses of one receiver give different vertical velocities without either being wrong. The Nevada Geodetic Laboratory now serves MIDAS velocities in IGS20 with 26 plate-fixed frames beside them, its IGS14 tables are superseded, its solutions are in the centre of mass frame with a translation to the centre of figure supplied, and the SONEL solutions PSMSL prints are in ITRF2014; at P224 the IGS20 and IGS14 tables differ by 0.26 mm per year and at Brest four solutions on one receiver span 1.28 mm per year. A velocity differenced against one from another frame or solution, or a modelled uplift compared with an observed one with neither frame stated, reads the frame as land motion."
tags: [gnss, gps, vertical-land-motion, reference-frame, igs20, igs14, itrf2014, plate-fixed, geocenter, midas, sonel, tide-gauge, sea-level]
generated: { by: knowledge-seeder/claude, at: 2026-09-15T17:50:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-15T18:32:59Z, role: maintainer, source: https://github.com/open-science-pillars/ocean-science/pull/60 }
severity: medium
dataset: ../connectors/gnss-vertical-velocity.md
status: stable
stale_after: 2027-03-15
sources:
  - id: blewitt-2004
    resource: https://geodesy.unr.edu/publications/Blewitt_verticals_2004.pdf
    title: "Blewitt, G. (2004), Fundamental ambiguity in the definition of vertical motion, Cahiers du Centre Europeen de Geodynamique et de Seismologie 23, 1 to 4 (read in full 2026-09-15 from the laboratory's site): vertical motion is not absolute but a matter of convention; a conventional terrestrial reference frame is defined implicitly by a set of station coordinates and their evolution; two groups adopting different station sets define vertical motion differently, and the differences are typically significant, much larger than the inherent measurement precision, especially where the two origins move relative to each other; in GPS practice the centre of figure frame is most common and the centre of mass frame is realised less precisely; a frame realised with or without scale rate gives different vertical motion; discrepancies between two analysis groups' vertical station velocities may reflect an inability to realise the same frame rather than systematic error; a model with an implicit frame is compared with observations by applying the same reference frame procedure to both"
  - id: blewitt-2003
    resource: https://geodesy.unr.edu/publications/Blewitt_Ref_Frame_2003.pdf
    title: "Blewitt, G. (2003), Self-consistency in reference frames, geocenter definition, and surface loading of the solid Earth, Journal of Geophysical Research 108(B2), 2103, doi:10.1029/2002JB002082 (abstract and introduction read 2026-09-15 from the laboratory's site): the centre of mass of the solid Earth, the centre of mass of the Earth system and the no-net-translation frames move relative to each other under a surface load, and how horizontal against vertical motion is read is tied to that choice"
  - id: ngl-home
    resource: https://geodesy.unr.edu/
    title: "The laboratory's home page (read 2026-09-15): MIDAS velocities in the IGS20 frame and in 26 plate-fixed frames defined by the Euler poles of Kreemer and others 2014, legacy NA12 and IGS08 tables, the IGS14 velocities kept under a separate link, all station pages and products now in IGS20, and the last IGS14 final solutions dated 2024-08-24"
  - id: ngl-acn-igs20
    resource: https://geodesy.unr.edu/gps/ngl.acn.IGS20.txt
    title: "The laboratory's GPS data analysis strategy summary, label GipsyX-2.3/IGS20 of 2024-08-25 (read 2026-09-15): daily coordinates transformed into IGS20 and into the plate-fixed frames using the plate rotation model of Kreemer and others 2014, from JPL final products carrying daily transformation parameters from the no-net-rotation frame to IGS20"
  - id: ngl-brst-station
    resource: https://geodesy.unr.edu/NGLStationPages/stations/BRST.sta
    title: "Nevada Geodetic Laboratory station page for BRST (read 2026-09-15): solutions offered in IGS20 and the EU plate frame, the note that NGL solutions are in CM with a CM to CF translation file supplied beside the loading predictions, and ten steps from equipment changes between 2006 and 2018"
  - id: midas-readme
    resource: https://geodesy.unr.edu/velocities/midas.readme.txt
    title: "The MIDAS velocity file README (read 2026-09-15): the velocities are provided in a number of frames named by code, the IGS frame and the plate frames from Africa to Woodlark, in one column layout"
  - id: igs14-readme
    resource: https://geodesy.unr.edu/velocities/README.txt
    title: "The velocities directory README (read 2026-09-15): the files there are in IGS14 and superseded by the IGS20 velocities under gps_timeseries/IGS20/midas/"
  - id: ngl-vlm
    resource: https://geodesy.unr.edu/vlm.php
    title: "The laboratory's vertical land motion at PSMSL tide gauges page (read 2026-09-15): the tide gauge rates built from the MIDAS rates the page links as the IGS14 table; at Brest the gauge's imaged rate is -1.136 mm per year with a formal uncertainty of 0.269, and the contributing station BRST at 0.29 km has a MIDAS rate of -1.136 with an uncertainty of 0.347 mm per year and a weight of 0.380 among five stations"
  - id: hammond-2021
    resource: https://geodesy.unr.edu/publications/HammondEtAl2021.pdf
    title: "Hammond, W. C., G. Blewitt, C. Kreemer and R. S. Nerem (2021), GPS Imaging of global vertical land motion for studies of sea level rise, Journal of Geophysical Research: Solid Earth 126, e2021JB022355, doi:10.1029/2021JB022355 (read 2026-09-15 from the laboratory's site: the abstract, the introduction, the data and rate estimation section and the discussion of Australia; the Crossref record verified the same day): the solutions are aligned to the IGS14 realisation of ITRF2014, and reference frame origin and geocenter drift are among the potential noise sources Riddell and others 2020 list for a continent-wide downward rate in Australia"
  - id: crossref-hammond
    resource: https://api.crossref.org/works/10.1029/2021JB022355
    title: "Crossref record read 2026-09-15: GPS Imaging of Global Vertical Land Motion for Studies of Sea Level Rise, Hammond, Blewitt, Kreemer and Nerem, Journal of Geophysical Research: Solid Earth, volume 126, issue 7, 2021"
  - id: psmsl-ellipsoid
    resource: https://psmsl.org/data/obtaining/ellipsoid.php
    title: "PSMSL, ellipsoidal links for RLR data (read 2026-09-15): all solutions provided use ITRF2014 and hence GRS80, which may change in the future; positive vertical rates mean the land is rising"
  - id: psmsl-rlr-diagram-brest
    resource: https://psmsl.org/data/obtaining/rlr.diagrams/1.php
    title: "PSMSL RLR diagram page for Brest (read 2026-09-15): four solutions on receiver BRST, ULR7a, JPL14, NGL14 and GT3, over 1998-10-31 to 2023-03-23, whose rates and uncertainties this bundle's land motion gotcha carries, spanning 1.28 mm per year"
  - id: connector
    resource: ../connectors/gnss-vertical-velocity.md
    title: "This bundle's GNSS vertical velocity connector concept: the tool serves the IGS20 and IGS14 tables by name and returns the frame, the table URL and the file date with every answer; at P224 the IGS20 table gives +0.214 plus or minus 0.386 mm per year and the IGS14 table -0.046 mm per year, a difference of 0.26 mm per year from the frame and two more years of data; a plate-fixed velocity is a different number from the same station's IGS velocity"
  - id: land-motion-gotcha
    resource: tide-gauge-relative-sea-level-and-land-motion.md
    title: "This bundle's gotcha on relative sea level: the four Brest solutions and the spread between them that exceeds each one's stated uncertainty"
  - id: gia-gotcha
    resource: tide-gauge-gia-is-modelled.md
    title: "This bundle's gotcha on the modelled GIA correction: the crustal uplift rate is the GNSS quantity of a model named by its ice history and Earth model"
---

# A vertical velocity carries its reference frame

**Mechanism.** Vertical motion is motion normal to a chosen horizontal
surface, and the surface, its origin and its evolution in time are
conventions realised by a set of station coordinates: two analyses
that adopt different station sets, different origin conventions or a
frame with and without a scale rate define different vertical
motions, and Blewitt states that the differences are typically
significant, much larger than the measurement precision, especially
where the two origins move relative to each other.[^blewitt-2004] The
origin choice is itself a family: the centre of mass of the solid
Earth, the centre of mass of the whole Earth system and the centre
of figure of the surface move relative to each other under a surface
load, and in GPS practice the centre of figure frame is the most
common while the centre of mass frame is realised less
precisely.[^blewitt-2003][^blewitt-2004] The laboratory's products
make the frame explicit. The current MIDAS velocities are in IGS20,
with 26 plate-fixed tables beside them defined by the Euler poles of
Kreemer and others 2014, legacy NA12 and IGS08 tables, and the IGS14
tables kept under a separate link and marked superseded, the last
IGS14 final solutions being dated 2024-08-24; the daily coordinates
are transformed into IGS20 and into the plate frames from JPL
products that carry daily no-net-rotation to IGS20 transformation
parameters.[^ngl-home][^igs14-readme][^ngl-acn-igs20][^midas-readme]
A station page offers the same station in IGS20 and in its plate
frame and notes that the solutions are in CM, with a CM to CF
translation supplied.[^ngl-brst-station] The tool serves the IGS20
and IGS14 tables by name and returns the frame, the table URL and the
file date with every answer, and a plate-fixed velocity is a
different number from the same station's IGS velocity.[^connector]
The sizes are recorded in this bundle. At P224 the IGS20 table gives
+0.214 plus or minus 0.386 mm per year and the IGS14 table -0.046 mm
per year, a difference of 0.26 mm per year that mixes the frame with
two more years of data.[^connector] The solutions PSMSL prints from
SONEL are in ITRF2014, and at Brest four of them on the one receiver
BRST, whose rates the land motion gotcha carries, spread over 1.28 mm
per year, more than each solution's stated uncertainty; the
laboratory's own tide gauge table, built from its IGS14 rates, puts
BRST at -1.136 mm per year.[^psmsl-ellipsoid][^psmsl-rlr-diagram-brest][^land-motion-gotcha][^ngl-vlm]
The gauge's imaged rate on that page is the same -1.136 mm per year,
because the weighted median of the five contributing stations falls
on BRST; the two numbers carry different uncertainties, 0.269 mm per
year for the gauge's formal uncertainty and 0.347 for BRST's MIDAS
rate.[^ngl-vlm]
Hammond and others 2021 align their solutions to the IGS14 realisation
of ITRF2014 and, discussing a continent-wide downward rate in
Australia, list reference frame origin and geocenter drift among the
noise sources that could produce it.[^hammond-2021][^crossref-hammond]

**Wrong-result mode.** A velocity from one table differenced against a
velocity from another, an IGS14 rate against an IGS20 rate, a
laboratory MIDAS rate against a SONEL solution, or a plate-fixed rate
against an IGS rate, and the difference read as land motion or as an
error in one of them, when Blewitt's statement is that two groups'
vertical velocities can differ from an inability to realise the same
frame with neither in error.[^blewitt-2004][^connector] A modelled
crustal uplift, the GNSS quantity of a GIA model, compared with an
observed rate with neither frame stated, so that the origin and scale
conventions of the model and of the frame enter the residual as
signal.[^blewitt-2004][^gia-gotcha] A sub-millimetre agreement or
disagreement between two solutions read as confirmation or as
systematic error at a station where the frame effect between the IGS
realisations is of that size.[^connector][^blewitt-2004] The trap is
visible rather than silent: the tool returns the frame with every
answer, the PSMSL diagram page names each solution, and the tables
are named by frame, so the error is a provenance omission that a
reader can recover, and the recorded difference between the IGS14
and IGS20 tables at one station, which mixes the frame with two more
years of data, sits below the stated
uncertainty.[^connector][^psmsl-rlr-diagram-brest]

**Correct approach.** A vertical velocity is quoted with its frame and
its table date, a difference between two velocities is taken within
one frame, both from the same table or both transformed into it, and
where the origin matters, at the sub-millimetre level or in an
average over a region, the origin convention (CM or CF) is stated as
the laboratory's station pages state it.[^connector][^ngl-brst-station][^blewitt-2004]
A modelled rate is compared with an observed one after the same
reference frame procedure is applied to both, which is Blewitt's
prescription, and the GIA model is named as the GIA gotcha
requires.[^blewitt-2004][^gia-gotcha] Where several solutions exist
for one receiver, as PSMSL prints for Brest, the spread across them
is reported beside the chosen solution's own uncertainty.[^psmsl-rlr-diagram-brest][^land-motion-gotcha]

**Verification.** The laboratory's home page, analysis strategy
summary, MIDAS README, velocities directory README, BRST station page
and vertical land motion page, Blewitt 2004 in full and the abstract
and introduction of Blewitt 2003 from the laboratory's site, the
abstract, introduction, data section and discussion of Hammond and
others 2021 from the same site, and PSMSL's
ellipsoidal links page and Brest RLR diagram page were read on
2026-09-15; the Hammond and others 2021 record was verified on
Crossref the same day.[^ngl-home][^ngl-acn-igs20][^midas-readme][^igs14-readme][^ngl-brst-station][^ngl-vlm][^blewitt-2004][^blewitt-2003][^hammond-2021][^crossref-hammond][^psmsl-ellipsoid][^psmsl-rlr-diagram-brest]
The P224 values are the connector concept's, read live on 2026-09-15
by its drafting session, and no velocity table was downloaded or
differenced here.[^connector]

[^blewitt-2004]: Blewitt, 2004, Fundamental ambiguity in the definition of vertical motion, read 2026-09-15
[^blewitt-2003]: Blewitt, 2003, Journal of Geophysical Research 108(B2), doi:10.1029/2002JB002082, abstract and introduction read 2026-09-15
[^ngl-home]: the laboratory's home page, read 2026-09-15
[^ngl-acn-igs20]: the laboratory's GipsyX-2.3/IGS20 analysis strategy summary, read 2026-09-15
[^ngl-brst-station]: Nevada Geodetic Laboratory station page for BRST, read 2026-09-15
[^midas-readme]: the MIDAS velocity file README, read 2026-09-15
[^igs14-readme]: the velocities directory README, read 2026-09-15
[^ngl-vlm]: the laboratory's vertical land motion at tide gauges page, read 2026-09-15
[^hammond-2021]: Hammond and others, 2021, Journal of Geophysical Research: Solid Earth 126, doi:10.1029/2021JB022355, read 2026-09-15
[^crossref-hammond]: Crossref record of Hammond and others 2021, read 2026-09-15
[^psmsl-ellipsoid]: PSMSL, ellipsoidal links for RLR data, read 2026-09-15
[^psmsl-rlr-diagram-brest]: PSMSL RLR diagram page for Brest (station 1), read 2026-09-15
[^connector]: this bundle's GNSS vertical velocity connector concept
[^land-motion-gotcha]: this bundle's tide gauge land motion gotcha
[^gia-gotcha]: this bundle's modelled GIA correction gotcha
