---
name: ocean-indices
description: "Climate ocean indices: ENSO Nino regions, NAO, PDO, AMO definitions, computation and baseline conventions."
user-invocable: false
---

# ocean-indices

Background expertise for climate indices, which are defined procedures,
not natural quantities.

## An index is its procedure

Region, variable, baseline, filtering, and detrending together ARE the
index; change any one and it is a different time series that happens to
share the name. Computing an index means implementing a specific
published definition and citing it; comparing indices means confirming
the definitions match.

## ENSO

- **Nino regions:** Nino3.4 (5S-5N, 170W-120W) is the default SST
  index region; Nino3 (150W-90W), Nino4 (160E-150W), Nino1+2
  (0-10S, 90W-80W) emphasize different flavors of events.
- **ONI** (the operational El Nino definition) is the 3-month running
  mean of Nino3.4 SST anomalies with a distinctive convention: the
  base period is a set of centered 30-year climatologies UPDATED every
  five years, so ONI values are not anomalies against one fixed
  baseline. Reproducing ONI requires reproducing that updating scheme.
- **Relative SST indices** (region anomaly minus tropical-mean
  anomaly) exist because a warming mean state inflates fixed-baseline
  indices; when classifying events across decades, name which family
  is in use.

## NAO

Two inequivalent families: station-based (Azores or Lisbon minus
Iceland sea level pressure; long records, fixed points, noisier) and
EOF-based (leading EOF of North Atlantic SLP; pattern adapts to the
data and era). They diverge in trend and variance behavior; sign
convention (positive = strengthened gradient) must be stated because
EOF signs are arbitrary until fixed.

## PDO

The leading EOF of North Pacific (poleward of 20N) monthly SST
anomalies WITH the global-mean SST anomaly removed first; skipping the
global-mean removal folds the warming trend into the "PDO" and is the
most common reproduction error. The projection index is standardized;
state the EOF training period.

## AMO / AMV

North Atlantic (commonly 0-60N) mean SST anomaly, where the detrending
choice is the scientific controversy: linear detrending, global-mean
removal, or forced-signal regression yield visibly different decadal
narratives. There is no neutral choice; name it and, for conclusions
that depend on it, show at least one alternative (the sensitivity
discipline mirrors mixed-layer's).

## Computation and baseline conventions

Anomalies follow the org's baseline rules: area-weighted regional
means (xarray-fundamentals), month-length weighting for annual values,
stated base periods, and cross-year seasonal handling per core's
calendars convention concept (conceptual reference; the core plugin is
a peer install). Running means lose endpoints and correlate adjacent
values; filtering is stated with window and type, and filtered series
inherit the autocorrelation caveats of basic-statistics' trend rules.

## Must NOT

- Never call a nonstandard region, baseline, or filtering by a
  standard index name.
- Never compare index series computed against different baselines or
  detrending choices as if interchangeable.
- Never compute PDO without removing the global-mean SST signal.
- Never present AMO conclusions without naming the detrending choice.
- Never smooth without stating window and type.
