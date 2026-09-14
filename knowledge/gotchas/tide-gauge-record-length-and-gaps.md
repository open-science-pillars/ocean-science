---
type: dataset-gotcha
spheres: [hydrosphere]
title: "A tide gauge trend carries its record length and its gaps"
description: "A linear trend from monthly mean sea level depends on how long the record is and where it is missing. CO-OPS computes its relative trends only from records spanning at least 30 years, and the confidence widths it publishes are about plus or minus 1.5 mm per year at 30 years and plus or minus 0.5 mm per year at 60 years, because interannual variability from coastal temperature, salinity, winds, pressure, currents and ENSO enters a short record as trend. PSMSL pads missing months with minus 99999, records the days missing from each month, drops an annual mean when more than one month is missing and flags suspect months and mean tide level substitutions. A trend quoted without its span, its gaps and a confidence interval is a number whose meaning is unknown."
tags: [tide-gauge, sea-level, trend, record-length, gaps, missing-data, confidence-interval, variability, psmsl, coops]
generated: { by: knowledge-seeder/claude, at: 2026-09-14T05:30:00Z }
severity: medium
dataset: ../connectors/psmsl-gauges.md
status: draft
stale_after: 2026-09-30
sources:
  - id: coops-sltrends
    resource: https://tidesandcurrents.noaa.gov/sltrends/sltrends.html
    title: "CO-OPS sea level trends page (read 2026-09-14): relative trends computed at 142 long-term stations from a minimum span of 30 years of monthly means; the page announces its retirement after 2026-09-30"
  - id: coops-sltrends-faq
    resource: https://tidesandcurrents.noaa.gov/sltrends/faq.html
    title: "CO-OPS sea level trends FAQ (read 2026-09-14): the 30-year minimum, the sources of long-term variation, the confidence widths of plus or minus 1.5 mm per year at 30 years and plus or minus 0.5 mm per year at 60 years attributed to NOAA Technical Report NOS CO-OPS 53, the overlap of confidence intervals between yearly recomputations and the effect of a few anomalous years"
  - id: coops-sltrends-station
    resource: https://tidesandcurrents.noaa.gov/sltrends/sltrends_station.shtml?id=8443970
    title: "CO-OPS station trend page template, read for Boston 8443970 on 2026-09-14: each trend stated with its 95 percent confidence interval and its start and end year, the interannual variation plots with the seasonal cycle and trend removed, the 50-year overlapping trends, and dashed lines bracketing questionable data or a possible datum shift"
  - id: psmsl-notes
    resource: https://psmsl.org/data/obtaining/notes.php
    title: "PSMSL notes on data and formats (read 2026-09-14): the monthly file columns, the minus 99999 padding of missing months, the 99 missing days of an interpolated month, the annual missing days flag, the dropped annual mean and the flags for attention"
  - id: psmsl-help
    resource: https://psmsl.org/data/obtaining/psmsl.hel
    title: "PSMSL help file (read 2026-09-14): a monthly value is calculated with 15 or fewer days missing, an annual mean is dropped with more than one month missing, and the 010 and 011 flags"
  - id: psmsl-station-brest
    resource: https://psmsl.org/data/obtaining/stations/1.php
    title: "PSMSL station page for Brest, station 1 (read 2026-09-14): time span 1807 to 2025, completeness 88 percent"
  - id: connector
    resource: ../connectors/psmsl-gauges.md
    title: "This bundle's PSMSL connector concept: the tool drops the minus 99999 sentinel and counts the months dropped"
  - id: coops-connector
    resource: ../connectors/coops-tides.md
    title: "This bundle's CO-OPS connector concept: the station water level record the CO-OPS trends, thresholds and confidence widths belong to, served on a declared datum"
---

# A tide gauge trend carries its record length and its gaps

**Mechanism.** CO-OPS, whose station records the connector
serves, computes relative sea level trends at 142 long-term stations
from a minimum span of 30 years of monthly means, and its FAQ states
that the minimum exists to account for long-term sea level variations
and to reduce the error of a trend computed from monthly
means.[^coops-sltrends][^coops-sltrends-faq][^coops-connector] The confidence
widths it publishes, from its report on sea level variations of the
United States from 1854 to 2006, are about plus or minus 1.5 mm per
year for a 30-year record and plus or minus 0.5 mm per year for a
60-year one; adding a few years mainly narrows the interval, the newest
trend is a little more precise and not necessarily more accurate, and
a few anomalously high or low recent years can move the value away
from the long-term trend.[^coops-sltrends-faq] The variability that
does this is interannual, from coastal temperature, salinity, wind,
atmospheric pressure and currents, and from ENSO at many Pacific
stations; CO-OPS plots it after removing the seasonal cycle and the
trend, and plots 50-year trends in overlapping windows against the
whole-record trend.[^coops-sltrends-station] Each station trend is
published with its 95 percent confidence interval and its start and
end year, and dashed lines on the plots bracket periods of
questionable data or a possible datum shift.[^coops-sltrends-station]
On the PSMSL side the completeness is in the file: a monthly file
lists the decimal year, the value in mm, the number of days missing
from the month and a flag; a month with no data inside the record's
span is padded with minus 99999, so the file covers the whole span; a
monthly mean is computed when 15 or fewer days are missing and an
interpolated month carries 99 missing days; an annual mean is dropped
when more than one month is missing and flagged when one month or at
least 30 days are; the flag 001 marks a value to be treated with
caution with the documentation read, and 010 an MTL value in an MSL
series.[^psmsl-notes][^psmsl-help] The Brest record spans 1807 to 2025
at 88 percent completeness, so about a month in eight is absent from
a two-century series.[^psmsl-station-brest] The connector's tool drops
the sentinel and counts the months it dropped.[^connector]

**Wrong-result mode.** A trend from a record shorter than the
variability it contains is a sample of that variability: at 30 years
the published width is plus or minus 1.5 mm per year, comparable to
the 1.7 to 1.8 mm per year the same FAQ cites from IPCC 2007 as the
past century's global rise, so a short-record trend can differ from
the long-term rate by its own size with no change in the
ocean.[^coops-sltrends-faq] A fit over a padded PSMSL file that treats
minus 99999 as a value is wrong by metres; a fit that drops the
sentinels without reporting where the gaps fall gives a trend whose
leverage sits in the populated part of the record, and a gap at one
end shortens the effective span without changing the nominal start
and end years.[^psmsl-notes] Two station trends compared without their
spans compare two windows of variability.

**Correct approach.** A gauge trend is stated with the start and end of
the record, the months present and absent and where the absences
fall, the flagged months included or excluded, a 95 percent confidence
interval as CO-OPS publishes one, and the same window when two
stations or two products are compared; a record under 30 years yields
variability rather than a rate in CO-OPS's
practice.[^coops-sltrends][^coops-sltrends-faq][^coops-connector][^psmsl-notes]

**Verification.** The CO-OPS sea level trends page, its FAQ and the
station page as rendered for Boston were read on 2026-09-14; the
confidence widths are quoted from the FAQ, which attributes them to
NOAA Technical Report NOS CO-OPS 53, not
read.[^coops-sltrends][^coops-sltrends-faq][^coops-sltrends-station]
The three CO-OPS trends pages carry a notice that the site retires
after 2026-09-30 in favour of a site the notice names as Sea Level
Trends and Extremes, in beta, without a URL in the fetched page, so
this concept's stale_after is that date and the numbers above are
to be re-read from the replacement site then.[^coops-sltrends]
PSMSL's notes page, help file and the Brest station page were read the
same day.[^psmsl-notes][^psmsl-help][^psmsl-station-brest] No data
were downloaded and no trend was computed.

[^coops-sltrends]: CO-OPS sea level trends page, read 2026-09-14
[^coops-sltrends-faq]: CO-OPS sea level trends FAQ, read 2026-09-14
[^coops-sltrends-station]: CO-OPS station trend page for Boston 8443970, read 2026-09-14
[^psmsl-notes]: PSMSL notes on data and formats, read 2026-09-14
[^psmsl-help]: PSMSL help file psmsl.hel, read 2026-09-14
[^psmsl-station-brest]: PSMSL station page for Brest (station 1), read 2026-09-14
[^connector]: This bundle's PSMSL connector concept
[^coops-connector]: This bundle's CO-OPS connector concept
