---
type: convention
title: "PDO index: North Pacific SST EOF with global-mean removed first"
description: "The Pacific Decadal Oscillation is the leading EOF of North Pacific (poleward of 20N) monthly SST anomalies AFTER removing the global-mean SST anomaly; skipping that removal is the most common reproduction error."
tags: [pdo, sst, eof, indices, climate, north-pacific]
timestamp: 2026-07-05
status: verified
verified: 2026-07-06
verified_by: OSP steward review
evidence:
  - https://www.ncei.noaa.gov/access/monitoring/pdo/
---

# PDO index: North Pacific SST EOF with global-mean removed first

The Pacific Decadal Oscillation is the leading EOF of North Pacific
(poleward of 20N) monthly SST anomalies, computed WITH the global-mean
SST anomaly removed first. The projection index is standardized; the
EOF training period is part of the definition and must be stated.

**Reproduction error (the common one).** Skipping the global-mean
removal folds the global warming trend into the "PDO" and is the most
common reproduction error. A PDO series computed without removing the
global-mean SST signal is not the PDO; it is a trend-contaminated
North Pacific SST index that happens to share the name. Removing the
global-mean SST anomaly first is not optional in this definition.
