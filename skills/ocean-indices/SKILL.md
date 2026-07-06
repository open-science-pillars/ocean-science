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
the definitions match. (Invariant method, not a dataset fact: it stays
here as procedure.)

## Consult the bundle for this index

Before computing ANY index, DISCOVER and consult the installed
knowledge bundle; do not work from a remembered definition, region box,
baseline rule, or reproduction caveat. Glob and grep
`knowledge/conventions/` (and the rest of `knowledge/`) by index name
(enso, nino, oni, nao, pdo, amo, amv) and by topic (region, baseline,
detrending, eof), read every concept that applies, and restate what
each fixes about the plan before computing, citing it by path. The
region coordinates, the ONI updating-baseline convention, the two NAO
families, the PDO global-mean-removal requirement, and the AMO
detrending controversy all live in concepts and are read from them, not
carried here. A concept added or corrected since you last ran is found
this way and changes this skill's behavior without editing it.

## Computation and baseline conventions

Anomalies follow the org's baseline rules: area-weighted regional
means (xarray-fundamentals), month-length weighting for annual values,
stated base periods, and cross-year seasonal handling per core's
calendars convention concept (conceptual reference; the core plugin is
a peer install). Running means lose endpoints and correlate adjacent
values; filtering is stated with window and type, and filtered series
inherit the autocorrelation caveats of basic-statistics' trend rules.
(Invariant method referencing peer conventions; no index-specific
numbers live here.)

## Must NOT (hard refusals)

These fire without consulting anything: each is invariant across
indices and eras, refusal-shaped, and wrong regardless of which product
supplied the SST or SLP field.

- Never call a nonstandard region, baseline, or filtering by a
  standard index name.
- Never compare index series computed against different baselines or
  detrending choices as if interchangeable.
- Never smooth without stating window and type.

Index-specific rules (the Nino region boxes and ONI baseline scheme,
the NAO family split and sign convention, the PDO global-mean-removal
requirement, the AMO detrending-naming discipline) are NOT restated
here: they live in `knowledge/conventions/` and are consulted per the
step above. That is what lets a corrected definition or a new index
concept change this skill's behavior without editing it.
