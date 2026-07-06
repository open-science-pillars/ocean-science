---
type: convention
title: "ENSO SST indices: Nino regions, ONI, and relative SST"
description: "Region boxes for Nino3.4/3/4/1+2, the ONI running-mean and updated-baseline convention, and the relative-SST family; each is a distinct published procedure."
tags: [enso, nino, oni, relative-sst, indices, climate, sst]
timestamp: 2026-07-05
status: draft
evidence:
  - "internal: relocated from ocean-science/skills/ocean-indices/SKILL.md during the knowledge-coupling migration, needs a steward evidence link"
---

# ENSO SST indices: Nino regions, ONI, and relative SST

**Nino regions.** Nino3.4 (5S-5N, 170W-120W) is the default SST index
region; Nino3 (150W-90W), Nino4 (160E-150W), and Nino1+2 (0-10S,
90W-80W) emphasize different flavors of events. Each region is a fixed
box; naming a series by one of these names asserts that box.

**ONI (Oceanic Nino Index).** The operational El Nino definition: the
3-month running mean of Nino3.4 SST anomalies, with a distinctive
convention: the base period is a set of centered 30-year climatologies
UPDATED every five years, so ONI values are not anomalies against one
fixed baseline. Reproducing ONI requires reproducing that updating
scheme; a single fixed baseline yields a different series that is not
ONI.

**Relative SST indices.** Region anomaly minus tropical-mean anomaly.
This family exists because a warming mean state inflates fixed-baseline
indices; when classifying events across decades, name which family
(fixed-baseline vs relative) is in use, because they disagree on event
counts in a warming climate.
