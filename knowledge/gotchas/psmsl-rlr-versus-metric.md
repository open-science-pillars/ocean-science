---
type: dataset-gotcha
spheres: [hydrosphere]
title: "PSMSL RLR records are reduced to one station datum and metric records are not"
description: "PSMSL holds two monthly series per station. The metric file is the means as received from the supplying authority, on a common datum within each year only; the Revised Local Reference (RLR) series is the same means reduced by PSMSL to a station datum about 7000 mm below mean sea level using the benchmark datum history the authority supplied. About two thirds of stations have an RLR series and the rest are metric only. A trend fitted to a metric series carries the station's gauge zero and benchmark changes as sea level, with nothing in the file to separate them, and PSMSL states that metric records serve the seasonal cycle only. The psmsl_monthly connector reads the RLR path."
tags: [psmsl, tide-gauge, rlr, metric, datum, sea-level, trend, revised-local-reference]
generated: { by: knowledge-seeder/claude, at: 2026-09-14T05:30:00Z }
severity: high
dataset: ../connectors/psmsl-gauges.md
eval_case: psmsl-rlr-versus-metric
status: draft
stale_after: 2027-03-14
sources:
  - id: psmsl-rlr
    resource: https://psmsl.org/data/obtaining/rlr.php
    title: "PSMSL, Revised Local Reference (RLR) definition (read 2026-09-14): the reduction to a common datum from the supplied datum history, the 7000 mm convention, the two thirds of stations that are RLR, the statement that metric records are not for time series or secular trends, and the German and Netherlands exceptions"
  - id: psmsl-help
    resource: https://psmsl.org/data/obtaining/psmsl.hel
    title: "PSMSL help file (read 2026-09-14): the metric file as the raw data as received with datum continuity required within a year only, separate RLR records where benchmark datums cannot be connected, mixed MTL and MSL records with differences over 10 cm, the 010 and 011 flags, and the correction applied in RLR but not in metric files"
  - id: psmsl-notes
    resource: https://psmsl.org/data/obtaining/notes.php
    title: "PSMSL notes on data and formats (read 2026-09-14): the three files of an RLR station and the one file of a metric-only station, the monthly file columns, the minus 99999 padding and the flag for attention"
  - id: psmsl-metric-list
    resource: https://psmsl.org/data/obtaining/metric.php
    title: "PSMSL, tide gauge stations with only metric data (extracted from the database 31 August 2026, read 2026-09-14): the statement that these records in general contain many jumps that make them unsuitable for time series analysis"
  - id: psmsl-station-brest
    resource: https://psmsl.org/data/obtaining/stations/1.php
    title: "PSMSL station page for Brest, station 1 (read 2026-09-14): 1807 to 2025, MTL data 1807 to 1835 with an MTL minus MSL of minus 23 mm, and the metric download labelled for use only with extreme caution"
  - id: psmsl-rlr-diagram-brest
    resource: https://psmsl.org/data/obtaining/rlr.diagrams/1.php
    title: "PSMSL RLR diagram page for Brest (read 2026-09-14): 2.459 m added to values 1807 to 1835 and 2.959 m to values from 1846 to refer them to RLR, which lies 12.500 m below primary benchmark NO-47"
  - id: psmsl-reference
    resource: https://psmsl.org/data/obtaining/reference.php
    title: "PSMSL referencing page (read 2026-09-14): the ten-author citation of Holgate and others 2013, Journal of Coastal Research 29(3), 493 to 504"
  - id: holgate-2013
    resource: https://doi.org/10.2112/JCOASTRES-D-12-00175.1
    title: "Holgate and others, New Data Systems and Products at the Permanent Service for Mean Sea Level, Journal of Coastal Research 29(3), 493 to 504 (Crossref record read 2026-09-14: title, journal, volume, issue and first page confirmed, registry date 2012-12-18, no author list in the record; the publisher's page was not fetched, the proxy having refused the redirect)"
  - id: connector
    resource: ../connectors/psmsl-gauges.md
    title: "This bundle's PSMSL connector concept: the psmsl_monthly tool reads the RLR monthly path and the tool drops and counts the minus 99999 sentinel"
---

# PSMSL RLR records are reduced to one station datum and metric records are not

**Mechanism.** PSMSL enters the monthly and annual means it receives
from almost 200 national authorities directly into a raw file per
station, the metric file; the means for any one year are required to
be on a common datum, datum continuity between years is not required
at that stage, and responsibility for the values rests with the
supplying authority.[^psmsl-help] To build a time series PSMSL reduces
the means to a common datum using the tide gauge datum history the
authority provides; about two thirds of the stations have been
adjusted this way and form the RLR dataset, whose datum at each
station is defined about 7000 mm below mean sea level so that the
values stay positive, and a record without a full benchmark datum
history stays metric only.[^psmsl-rlr] The reduction is an offset per
period of the datum history: the Brest RLR diagram adds 2.459 m to the
values from 1807 to 1835 and 2.959 m to the values from 1846 onwards
to refer them to RLR, which lies 12.500 m below the primary benchmark
NO-47.[^psmsl-rlr-diagram-brest] Where the benchmark datums of two
epochs of one station cannot be geodetically connected, PSMSL keeps
them as separate RLR records rather than joining them.[^psmsl-help]
The two files differ in a second way: where a record mixes mean tide
level (MTL) with mean sea level (MSL), a difference that exceeds 10 cm
in the extreme cases, the RLR series carries an MTL to MSL correction
and the flag 010 on the affected months, and the metric file carries
the flag without the correction.[^psmsl-help] Brest shows this: MTL
data from 1807 to 1835 with an MTL minus MSL of minus 23
mm.[^psmsl-station-brest] An RLR station has three files (monthly RLR,
annual RLR, monthly metric) and a metric-only station has one, there
being no metric annual means because PSMSL states they have no
application.[^psmsl-notes] The metric station list, extracted from the
database on 31 August 2026, states that these records in general
contain many jumps that make them unsuitable for time series
analysis.[^psmsl-metric-list] The connector's psmsl_monthly tool reads
the RLR monthly path.[^connector]

**Wrong-result mode.** A secular trend from a metric file is the sum of
sea level change and every gauge zero change, re-levelling and
benchmark change in the station's history, and PSMSL's stated position
is that metric records serve studies of the seasonal cycle only and
not time series analysis or secular trends.[^psmsl-rlr] The failure is
silent: a metric monthly file has the same columns as an RLR file
(decimal year, value in mm, missing days, flag), the values are
plausible heights and a fit returns a number.[^psmsl-notes] A
metric-only station has no RLR series to compare against, so the jump
is not visible from PSMSL's own files. A comparison of a metric value
against an RLR value, or of two stations' metric values, compares
datums. The exceptions are documented per station and not general: a
German metric record referenced to Normal Null, which PSMSL states is
in effect on a local level, or a Netherlands record on NAP, which
PSMSL has reclassified as RLR with separate factors before and after
the 2005 re-levelling, is usable with the station comment
read.[^psmsl-rlr]

**Correct approach.** A trend or a difference from PSMSL rests on the
RLR series, read from the RLR monthly or annual path, and the record's
status (RLR, or metric only) is stated beside the trend; a metric-only
station contributes a seasonal cycle and no trend; a station with more
than one RLR record is one record per fit unless PSMSL's documentation
names the pair as a composite; the flag column is read, and the months
flagged 011, an MTL value whose correction PSMSL calls uncertain beyond
1 cm, are outside a long-term trend as PSMSL
recommends.[^psmsl-help][^psmsl-notes] The RLR values are heights above
an arbitrary local datum, so differences and trends are the
quantities, as the connector concept states.[^connector]

**Verification.** PSMSL's RLR definition page, help file, notes page
and metric station list were read on 2026-09-14, as were the Brest
station page (station 1, 1807 to 2025) and its RLR diagram page with
the two RLR
offsets.[^psmsl-rlr][^psmsl-help][^psmsl-notes][^psmsl-metric-list][^psmsl-station-brest][^psmsl-rlr-diagram-brest]
The data description paper, Holgate and others 2013, is cited through
its registry record: Crossref places it in the Journal of Coastal
Research, volume 29, issue 3, first page 493, with a registry date of
2012-12-18 and no author list; the ten authors and the page range 493
to 504 are from PSMSL's referencing page, and the publisher's page was
not fetched because the drafting environment's proxy refused the
redirect.[^holgate-2013][^psmsl-reference] No data file was
downloaded.

[^psmsl-rlr]: PSMSL, Revised Local Reference definition, read 2026-09-14
[^psmsl-help]: PSMSL help file psmsl.hel, read 2026-09-14
[^psmsl-notes]: PSMSL notes on data and formats, read 2026-09-14
[^psmsl-metric-list]: PSMSL metric-only station list, extracted 31 August 2026, read 2026-09-14
[^psmsl-station-brest]: PSMSL station page for Brest (station 1), read 2026-09-14
[^psmsl-rlr-diagram-brest]: PSMSL RLR diagram page for Brest, read 2026-09-14
[^psmsl-reference]: PSMSL referencing page, read 2026-09-14
[^holgate-2013]: Holgate and others, 2013, Journal of Coastal Research, doi:10.2112/JCOASTRES-D-12-00175.1, Crossref record read 2026-09-14
[^connector]: This bundle's PSMSL connector concept
