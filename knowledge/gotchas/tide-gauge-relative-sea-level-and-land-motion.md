---
type: dataset-gotcha
spheres: [hydrosphere, geosphere]
title: "A tide gauge trend is relative sea level and carries the land's vertical motion"
description: "A tide gauge measures the water against a benchmark on the local land, so its series, a PSMSL RLR record or a CO-OPS station, is relative sea level, the sum of sea surface change and vertical land motion at the gauge, while altimetry measures the sea surface against the ellipsoid. A gauge trend compared with an altimetry trend, or used as a sea level record, differs from the sea surface change by the land motion, which reaches more than 10 mm per year of subsidence on the northern Gulf coast and makes relative sea level fall in southeastern Alaska; at Brest four GNSS solutions on one receiver give minus 0.22 to minus 1.50 mm per year. The comparison is not a sea level comparison until the land motion, its source and its uncertainty are stated."
tags: [tide-gauge, relative-sea-level, vertical-land-motion, gnss, altimetry, psmsl, coops, sea-level, trend]
generated: { by: knowledge-seeder/claude, at: 2026-09-14T05:30:00Z }
severity: high
dataset: ../connectors/psmsl-gauges.md
eval_case: tide-gauge-relative-sea-level-and-land-motion
status: draft
stale_after: 2027-03-14
sources:
  - id: psmsl-ellipsoid
    resource: https://psmsl.org/data/obtaining/ellipsoid.php
    title: "PSMSL, ellipsoidal links for RLR data (read 2026-09-14): RLR heights as relative mean sea level measured against the local land, the need to remove land movement for a reconstruction and to know the datum height above the ellipsoid for a comparison with altimetry, the GNSS link through levelling, the SONEL collaboration and the ITRF2014 and GRS80 frame"
  - id: psmsl-rlr-diagram-brest
    resource: https://psmsl.org/data/obtaining/rlr.diagrams/1.php
    title: "PSMSL RLR diagram page for Brest, station 1 (read 2026-09-14): the ellipsoidal information from SONEL for receiver BRST, four solutions with their vertical rates, uncertainties, datum heights, epoch, span and distance to the gauge"
  - id: psmsl-station-brest
    resource: https://psmsl.org/data/obtaining/stations/1.php
    title: "PSMSL station page for Brest (read 2026-09-14): the link to ellipsoid marked available and the nearby SONEL GNSS stations named"
  - id: psmsl-gia
    resource: https://psmsl.org/train_and_info/geo_signals/gia/
    title: "PSMSL, glacial isostatic adjustment (read 2026-09-14): GIA changes the sea surface as well as the crust, so a correction for crustal motion alone removes only part of it"
  - id: coops-sltrends
    resource: https://tidesandcurrents.noaa.gov/sltrends/sltrends.html
    title: "CO-OPS sea level trends page (read 2026-09-14): trends from tide gauges are local relative sea level trends, measured against a fixed reference on land, the combination of sea level rise and local vertical land motion; the page announces its retirement after 2026-09-30"
  - id: coops-sltrends-faq
    resource: https://tidesandcurrents.noaa.gov/sltrends/faq.html
    title: "CO-OPS sea level trends FAQ (read 2026-09-14): a tide station's measurements include both global sea level rise and vertical land motion, relative trends above 10 mm per year on the northern Gulf coast from subsidence and falling relative sea level in southeastern Alaska from isostatic rebound"
  - id: coops-sltrends-station
    resource: https://tidesandcurrents.noaa.gov/sltrends/sltrends_station.shtml?id=8443970
    title: "CO-OPS station trend page template, read for Boston 8443970 on 2026-09-14: a negative relative trend does not mean the ocean surface is falling but that the land rises faster than the ocean"
  - id: gia-gotcha
    resource: tide-gauge-gia-is-modelled.md
    title: "This bundle's companion gotcha on the GIA correction as a model prediction"
  - id: connector
    resource: ../connectors/psmsl-gauges.md
    title: "This bundle's PSMSL connector concept, which carries the RLR datum facts and not the land motion"
  - id: coops-connector
    resource: ../connectors/coops-tides.md
    title: "This bundle's CO-OPS connector concept, which carries the datum facts of the service and not the land motion"
---

# A tide gauge trend is relative sea level and carries the land's vertical motion

**Mechanism.** PSMSL's RLR series are heights above a local datum fixed
to a geodetic benchmark assumed to be on reasonably stable ground;
PSMSL names them relative mean sea level, height measured relative to
the local land, and states that the data can be affected by vertical
movement of the land.[^psmsl-ellipsoid] CO-OPS states the same of its
stations: the measurements are made with respect to a local fixed
reference on land, and a relative sea level trend is the combination
of sea level rise and local vertical land motion, whether subsidence,
glacial rebound or tectonic motion.[^coops-sltrends][^coops-sltrends-faq]
The size is regional: relative trends above 10 mm per year in parts of
the northern Gulf coast where subsidence is large, and falling
relative sea level in southeastern Alaska where the land rises by
isostatic rebound; a negative trend does not mean the sea surface is
falling.[^coops-sltrends-faq][^coops-sltrends-station] A comparison
with satellite altimetry needs the height of the gauge datum above the
Earth-centred ellipsoid, and a reconstruction of global mean sea level
from gauges needs the land movement removed at each site; where
levelling connects the benchmark to a nearby GNSS receiver, PSMSL and
SONEL publish on the station's RLR diagram page the RLR datum height
above the ellipsoid (ITRF2014, GRS80), the linear rate of vertical
land movement with its uncertainty, the epoch, the GNSS span and the
distance from the gauge.[^psmsl-ellipsoid] Brest carries such a link:
the BRST receiver, 293 m from the gauge, with data from 1998-10-31 to
2023-03-23, and four solutions (ULR7a, JPL14, NGL14, GT3) whose
vertical rates are minus 0.22 plus or minus 0.17, minus 1.12 plus or
minus 0.23, minus 1.09 plus or minus 0.41 and minus 1.50 plus or minus
0.30 mm per year, with RLR datum heights of 44.073 to 44.094 m above
the ellipsoid at epoch 2020.0.[^psmsl-rlr-diagram-brest] The spread
between the solutions on one receiver exceeds the stated uncertainty
of each. Glacial isostatic adjustment is one contributor to the land
motion and a modelled correction of its own, and a GNSS rate removes
the crustal motion at the gauge only: PSMSL notes that GIA also changes
the sea surface, so a correction for crustal motion removes only part
of it.[^psmsl-gia][^gia-gotcha]

**Wrong-result mode.** A gauge trend set beside an altimetry trend, or
an altimetry field validated against gauges, with no land motion term
compares two different quantities, and the difference between them is
read as an altimeter bias, a coastal signal or a discrepancy when it
is the land. The failure is silent in both directions: an RLR series
and an altimetry series are both millimetres with a trend, and nothing
in an RLR file carries the land motion. A gauge trend quoted as the
sea level rise at a place is relative sea level, and at a subsiding or
rebounding coast it differs from the sea surface change by more than
the sea level signal itself.[^coops-sltrends-faq] A land motion rate
taken from one GNSS solution as if it were the rate carries that
solution's choice, and at Brest the choice moves the rate by more than
1 mm per year.[^psmsl-rlr-diagram-brest]

**Correct approach.** A gauge trend is named relative sea level with its
station and datum, and a comparison with altimetry, or a use of the
gauge as an absolute sea level record, states the vertical land motion
applied, its source (a GNSS solution by its identifier, span and
distance from the gauge, or a model), its uncertainty and the residual
sea surface part of GIA where it matters, so that the same quantity
stands on both sides.[^psmsl-ellipsoid][^psmsl-gia] The PSMSL station
page states whether an ellipsoidal link exists and the RLR diagram
page carries the numbers.[^psmsl-station-brest][^psmsl-rlr-diagram-brest]
The connector concepts carry the datum facts of each service and not
the land motion.[^connector][^coops-connector]

**Verification.** PSMSL's ellipsoidal links page, GIA page, Brest
station page and Brest RLR diagram page, and CO-OPS's sea level trends
page, its FAQ and the station trend page as rendered for Boston, were
read on 2026-09-14; the four Brest GNSS rates are as printed on the
RLR diagram page, which attributes them to SONEL, whose site was not
visited.[^psmsl-ellipsoid][^psmsl-gia][^psmsl-station-brest][^psmsl-rlr-diagram-brest][^coops-sltrends][^coops-sltrends-faq][^coops-sltrends-station]
The CO-OPS sea level trends site announces its own retirement after
2026-09-30 in favour of a new site, so the CO-OPS URLs cited are
dated.[^coops-sltrends] No data were downloaded.

[^psmsl-ellipsoid]: PSMSL, ellipsoidal links for RLR data, read 2026-09-14
[^psmsl-rlr-diagram-brest]: PSMSL RLR diagram page for Brest, read 2026-09-14
[^psmsl-station-brest]: PSMSL station page for Brest (station 1), read 2026-09-14
[^psmsl-gia]: PSMSL, glacial isostatic adjustment page, read 2026-09-14
[^coops-sltrends]: CO-OPS sea level trends page, read 2026-09-14
[^coops-sltrends-faq]: CO-OPS sea level trends FAQ, read 2026-09-14
[^coops-sltrends-station]: CO-OPS station trend page for Boston 8443970, read 2026-09-14
[^gia-gotcha]: This bundle's gotcha on the modelled GIA correction
[^connector]: This bundle's PSMSL connector concept
[^coops-connector]: This bundle's CO-OPS connector concept
