---
type: dataset-gotcha
spheres: [hydrosphere]
title: "CO-OPS water levels are heights above a chosen datum on the 1983 to 2001 epoch"
description: "Every CO-OPS water level is a height above the datum named in the request (MLLW, MSL, NAVD88, the station datum and others), and the tidal datums are means over the National Tidal Datum Epoch, at present 1983 through 2001, with a 2002 to 2020 epoch scheduled for release in 2029. At Boston the datums sit 3.53 ft (MLLW), 8.73 ft (MSL) and 9.03 ft (NAVD88) above the station datum, so one water level differs by 5.5 ft between MLLW and NAVD88, and because each tidal datum is local to its station two stations' heights compare only on one datum."
tags: [coops, tides, water-level, datum, mllw, navd88, station-datum, ntde, epoch]
generated: { by: knowledge-seeder/claude, at: 2026-09-14T05:30:00Z }
severity: medium
dataset: ../connectors/coops-tides.md
status: draft
stale_after: 2027-03-14
sources:
  - id: coops-datums
    resource: https://tidesandcurrents.noaa.gov/datum_options.html
    title: "CO-OPS tidal datums page (read 2026-09-14): the definitions of MLLW, MSL, the station datum and the National Tidal Datum Epoch, the modified 5-year epoch, NAVD88 as a geodetic datum not to be used as mean sea level, and the statement that tidal datums are local"
  - id: coops-ntde
    resource: https://tidesandcurrents.noaa.gov/datum-updates/ntde/
    title: "CO-OPS National Tidal Datum Epoch page (read 2026-09-14): the 19-year epoch, the current 1983 to 2001 epoch, its replacement based on 2002 to 2020 and the proposed 2029 release"
  - id: coops-ntde-faq
    resource: https://tidesandcurrents.noaa.gov/datum-updates/ntde/faq.html
    title: "CO-OPS NTDE frequently asked questions (read 2026-09-14): the 0.10 ft update threshold, the 18.6-year nodal cycle behind the 19 years, the roughly 2,000 stations re-processed at once and the expected 6 to 7 cm change in predictions"
  - id: coops-api
    resource: https://api.tidesandcurrents.noaa.gov/api/prod/
    title: "CO-OPS data API documentation (read 2026-09-14): the datum parameter mandatory for every water level product, its options and their notes, and the datums product moved to the metadata API"
  - id: coops-mdapi
    resource: https://api.tidesandcurrents.noaa.gov/mdapi/prod/
    title: "CO-OPS metadata API documentation (read 2026-09-14): the datum collection per station with its epoch, acceptance date, orthometric datum and values, and the superseded datums of the previous epoch"
  - id: coops-boston-datums
    resource: https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/8443970/datums.json
    title: "The Boston (8443970) datum collection from the metadata API (read 2026-09-14): epoch 1983 to 2001, accepted 17 April 2003, in feet, STND 0.0, MLLW 3.53, MSL 8.73, MHHW 13.8, NAVD88 9.03"
  - id: connector
    resource: ../connectors/coops-tides.md
    title: "This bundle's CO-OPS connector concept: the coops_data tool requires the datum and returns it in every response"
---

# CO-OPS water levels are heights above a chosen datum on the 1983 to 2001 epoch

**Mechanism.** A tidal datum is a standard elevation defined by a phase
of the tide, computed from observations at a station over the National
Tidal Datum Epoch and referenced to bench marks: MLLW is the mean of
the lower low water of each tidal day over the epoch, MSL the mean of
the hourly heights over the epoch, and the station datum a fixed base
elevation unique to each station, set below any level the water is
expected to reach, referenced to the primary bench mark and held
constant through changes of gauge or staff.[^coops-datums] The epoch
is the 19-year period the National Ocean Service adopts, at present
1983 through 2001, considered for revision every 20 to 25 years, and
regions with anomalous sea level change (Alaska, the Gulf coast) use a
modified 5-year epoch.[^coops-datums] The 19 years span the 18.6-year
cycle of the lunar nodes.[^coops-ntde-faq] NAVD88 is a geodetic datum
from levelling, and the datums page states that it should not be used
as mean sea level.[^coops-datums] The data API makes the datum
mandatory for every water level product and offers CRD, IGLD, LWD,
MHHW, MHW, MTL, MSL, MLW, MLLW (the nautical chart datum for all US
coastal waters and the only datum for subordinate prediction
stations), NAVD (not available at every station) and STND, the
station datum all data are collected to; the datums themselves are
served by the metadata API.[^coops-api] That API returns a datum
collection per station with its epoch, its acceptance date, the
orthometric datum and each datum's value, and the previous epoch's set
under superseded datums.[^coops-mdapi] The Boston record (station
8443970, epoch 1983 to 2001, accepted 17 April 2003, in feet) reads
STND 0.0, MLLW 3.53, MSL 8.73, MHHW 13.8 and NAVD88
9.03.[^coops-boston-datums] The current epoch is being replaced by one
based on 2002 to 2020, with the datums and bench mark sheets of about
2,000 stations proposed for release together in 2029; an update is
triggered by an average national difference of 0.10 ft (0.03 m), and
predictions are expected to change by about 6 to 7 cm at most
locations.[^coops-ntde][^coops-ntde-faq] Tidal datums are local: the
datums page states that they are not to be extended into areas of
differing oceanographic characteristics without substantiating
measurements.[^coops-datums]

**Wrong-result mode.** Two water levels from two stations on MLLW
differ by the difference of two local tidal datums as well as by the
water, and at one station a level on MLLW and the same level on NAVD88
differ by 5.5 ft at Boston.[^coops-boston-datums] A series on a tidal
datum that spans the 2029 epoch change carries the re-computation of
the datum as a step, since the whole published set changes at
once.[^coops-ntde-faq] A level quoted without its datum is not a
height. The connector concept names this trap and states that the tool
requires the datum and returns it in every response, which is why the
error is visible in the record rather than silent.[^connector]

**Correct approach.** A level or a series carries its station, its
datum and the epoch of that datum, read from the response and the
metadata API; a comparison across stations rests on one datum, a
geodetic one (NAVD88 where the station has it) for a comparison of
heights and a tidal one for a comparison of tidal state, with the
station's datum collection supplying the offsets between them; a
series that crosses an epoch change names the epoch of each
part.[^coops-api][^coops-mdapi]

**Verification.** The datums page, the NTDE page and its FAQ, the data
API documentation for the datum parameter and the metadata API
documentation were read on 2026-09-14, and the Boston datum collection
was read from the metadata API the same
day.[^coops-datums][^coops-ntde][^coops-ntde-faq][^coops-api][^coops-mdapi][^coops-boston-datums]
No water level data were downloaded.

[^coops-datums]: CO-OPS tidal datums page, read 2026-09-14
[^coops-ntde]: CO-OPS National Tidal Datum Epoch page, read 2026-09-14
[^coops-ntde-faq]: CO-OPS NTDE frequently asked questions, read 2026-09-14
[^coops-api]: CO-OPS data API documentation, read 2026-09-14
[^coops-mdapi]: CO-OPS metadata API documentation, read 2026-09-14
[^coops-boston-datums]: Boston 8443970 datum collection, metadata API, read 2026-09-14
[^connector]: This bundle's CO-OPS connector concept
