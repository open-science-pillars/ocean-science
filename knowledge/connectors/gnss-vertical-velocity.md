---
type: connector
title: "GNSS vertical land motion: the Nevada Geodetic Laboratory MIDAS velocity table (observations server)"
description: "A station's vertical velocity, its uncertainty and its reference frame through gnss_vertical_velocity, by station id or by the station nearest a point: the laboratory's MIDAS table for the IGS20 frame, 21,821 stations in 27 columns rebuilt weekly, velocities in metres per year in the file and millimetres per year in the tool, longitudes written below -180 for eastern stations, and a superseded IGS14 table kept beside it. The up velocity is the land motion a tide gauge series carries; a plate-fixed velocity is a different number."
tags: [connector, gnss, gps, vertical-land-motion, midas, ngl, geodesy, tide-gauge, sea-level, mcp, observations]
generated: { by: process:claude-code, at: 2026-09-15T14:00:00Z }
status: draft
citation:
  access_date_required: true
  authority: https://geodesy.unr.edu/
  data: "Nevada Geodetic Laboratory MIDAS velocity table, IGS20 frame (midas.IGS.txt, rebuilt weekly), accessed {access_date}"
  paper: "Blewitt, G., W. C. Hammond and C. Kreemer (2018), Harnessing the GPS Data Explosion for Interdisciplinary Science, Eos, 99"
  doi: "10.1029/2018EO104623"
  method: "Blewitt, G., C. Kreemer, W. C. Hammond and J. Gazeaux (2016), MIDAS robust trend estimator for accurate GPS station velocities without step detection, Journal of Geophysical Research: Solid Earth, 121, doi:10.1002/2015JB012552"
  note: "the laboratory asks that the Eos paper be cited for its data products and the MIDAS paper for the velocities, and that a station's original data citation be referenced where one exists; both DOIs verified on Crossref 2026-09-15 (titles, authors, journals, years)"
stale_after: 2027-03-15
sources:
  - id: midas-readme
    resource: https://geodesy.unr.edu/velocities/midas.readme.txt
    title: "The MIDAS velocity file README, read 2026-09-15: the citation, weekly rebuilding, and the 27 columns (station, version, first and last epoch in decimal years, duration, epoch counts, velocity pairs, east north up velocities and uncertainties in m/yr, offsets, outlier fractions, pair standard deviations, steps assumed, latitude, longitude, height) and the plate frame codes"
  - id: igs14-readme
    resource: https://geodesy.unr.edu/velocities/README.txt
    title: "The velocities directory README, read 2026-09-15: the files there are IGS14 and superseded by the IGS20 velocities under gps_timeseries/IGS20/midas/"
  - id: igs20-table
    resource: https://geodesy.unr.edu/gps_timeseries/IGS20/midas/midas.IGS.txt
    title: "The IGS20 MIDAS table read 2026-09-15 (Last-Modified 2026-09-15 00:01:17 GMT, 5.4 MB): 21,821 stations, every line 27 columns; P224 (Berkeley, 37.8639N 122.2191W) up +0.214 mm/yr with uncertainty 0.386 mm/yr over 2005.17 to 2026.68 with five steps assumed; TIBB (Tiburon) up -0.948 mm/yr with uncertainty 0.397 mm/yr since 1995.21; eastern stations such as 00NA at 130.844E written with longitude -229.156"
  - id: igs14-table
    resource: https://geodesy.unr.edu/velocities/midas.IGS14.txt
    title: "The IGS14 MIDAS table read 2026-09-15 (Last-Modified 2024-11-04, 5.0 MB): 20,168 stations in the same 27 columns; P224 up -0.046 mm/yr there over 2005.17 to 2024.74, the difference with the IGS20 value being the frame and two more years of data"
  - id: ngl-home
    resource: https://geodesy.unr.edu/
    title: "The laboratory's home page, read 2026-09-15: the citation statement for data products (Blewitt, Hammond and Kreemer 2018, Eos), the note that many stations carry an original data citation, the IGS20 frame as the current MIDAS field, the plate frames defined by the Euler poles of Kreemer et al. 2014, and the directory reorganisation that places IGS20 products under gps_timeseries/IGS20/"
  - id: crossref-midas
    resource: https://api.crossref.org/works/10.1002/2015JB012552
    title: "Crossref record read 2026-09-15: MIDAS robust trend estimator for accurate GPS station velocities without step detection, Blewitt, Kreemer, Hammond and Gazeaux, Journal of Geophysical Research: Solid Earth, 2016"
  - id: crossref-eos
    resource: https://api.crossref.org/works/10.1029/2018EO104623
    title: "Crossref record read 2026-09-15: Harnessing the GPS Data Explosion for Interdisciplinary Science, Blewitt, Hammond and Kreemer, Eos, 2018"
  - id: land-motion-gotcha
    resource: ../gotchas/tide-gauge-relative-sea-level-and-land-motion.md
    title: "This bundle's gotcha: a tide gauge trend is relative sea level and carries the land's vertical motion, the PSMSL ellipsoidal links through SONEL, and the frame those links are given in"
  - id: server
    resource: https://github.com/open-science-pillars/core/blob/9fad9ab515e05aef5be73076ef24ca4a9ad83f5f/connectors/observations_mcp.py
    title: "The observations server carrying gnss_vertical_velocity (contract 0.5.0): the table read once per process, the parser on the README columns, the nearest-station lookup, and the recorded fixture (the table's first three lines and every station within 1.5 degrees of the San Francisco Bay, 262 lines of 21,821)"
---

# GNSS vertical land motion: the MIDAS velocity table

`gnss_vertical_velocity` reads one station's velocity from the Nevada
Geodetic Laboratory's MIDAS velocity table, anonymous over HTTPS, by
the laboratory's 4-character station id or by the station nearest a
latitude and longitude, and returns the up velocity, its uncertainty,
the east and north components, the epochs, the steps assumed and the
frame.[^igs20-table][^server] Verified live 2026-09-15 at P224 in
Berkeley by id and by coordinates.[^igs20-table]

**The table, the frame and the date.** The current table is the IGS20
one under `gps_timeseries/IGS20/midas/midas.IGS.txt`, rebuilt weekly
(Last-Modified 2026-09-15 on the day it was read), 21,821 stations in
27 columns with no header.[^igs20-table][^midas-readme] The IGS14
table under `velocities/` is superseded and dated 2024-11-04; the
laboratory's own README there says so.[^igs14-readme][^igs14-table]
The tool serves both by name and returns the frame, the table URL and
the file's last modification with every answer, because a velocity
without its frame and date cannot be joined to another.[^server] A
velocity in a plate-fixed frame (the NA, EU, PA and other tables)
is a different number from the same station's IGS velocity; the tool
serves the IGS frames only.[^midas-readme][^ngl-home]

**Units and columns.** The file writes velocities and uncertainties
in metres per year in columns 9 to 14 (east, north, up, then their
uncertainties); the tool returns millimetres per year.[^midas-readme]
Longitudes in columns 25 and 26 are written below -180 for eastern
stations (00NA in Darwin at 130.844E appears as -229.156), so a
nearest-station search normalises them first.[^igs20-table] The
uncertainty is the MIDAS estimator's own, from the distribution of
velocity pairs; the count of pairs and of steps assumed travel with
it.[^midas-readme]

**What the up velocity is.** At P224 the IGS20 table gives
+0.214 mm/yr with an uncertainty of 0.386 mm/yr over 21.5 years; the
IGS14 table gave -0.046 mm/yr over 19.6 years.[^igs20-table][^igs14-table]
The difference is the frame and the added years, and it is of the
size of the uncertainty: a vertical rate under a millimetre a year is
not distinguishable from zero at one station, and a tide gauge
correction built from it inherits that.[^igs20-table] A tide gauge
measures the water against the local land, so its trend is relative
sea level and carries this vertical motion; the PSMSL ellipsoidal
links give the gauge's own GNSS solutions through SONEL in their
frame, and the nearest MIDAS station is a different station at a
different distance from the gauge.[^land-motion-gotcha]

**Cost.** The table is one request of 5.4 MB, read once per process
and matched locally; the station id and the coordinates never leave
the machine.[^server]

**Composition.** The land's vertical motion beside the tide gauge
trend and the altimetry trend: the term that separates relative from
absolute sea level, with its frame and its uncertainty
stated.[^land-motion-gotcha]

[^midas-readme]: the MIDAS velocity file README, read 2026-09-15
[^igs14-readme]: the velocities directory README, read 2026-09-15
[^igs20-table]: the IGS20 MIDAS table, read 2026-09-15
[^igs14-table]: the IGS14 MIDAS table, read 2026-09-15
[^ngl-home]: the laboratory's home page, read 2026-09-15
[^crossref-midas]: Crossref record of the MIDAS paper, read 2026-09-15
[^crossref-eos]: Crossref record of the Eos paper, read 2026-09-15
[^land-motion-gotcha]: this bundle's tide gauge land motion gotcha
[^server]: the observations server source
