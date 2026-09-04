# SWOT KaRIn L2 SSH products: procedure and pointers

Reference for the swot skill. This file is procedure over the knowledge
concepts; the product inventory (ShortNames, concept ids, version
families and their holdings), the granule anatomy, the orbit phases,
and the current processing baseline are read from the concepts named
below, never from here.

## Where the facts live

- Identity and swath geometry, granule structure, the Variants table
  (tiers by version family with concept ids), the family holdings, the
  nadir altimeter collections, the uncertainty variables, and the known
  issues (baseline drift within collections, the unapplied crossover
  correction, the whole-pass spatial-search caveat):
  `knowledge/snapshot-podaac/datasets/swot-karin.md`.
- Orbit phases, cycle numbering, and the version-family trap (the
  cal/val era lives only in the D family; an empty early-mission result
  is a family symptom before it is a coverage fact):
  `knowledge/snapshot-podaac/gotchas/swot-calval-orbit-phases.md`.
- The crossover correction and its quality gate:
  `knowledge/snapshot-podaac/gotchas/swot-crossover-unapplied.md`.
- Hydrology products (river and lake vector products, rasters) are
  separate SWOT collections, deferred to the hydrology plugin.

## Procedure

1. Choose the tier from the dataset concept's Variants table by what
   the analysis needs (SSH anomaly with core flags; the full correction
   and uncertainty set; wind and wave state; the finest posting), and
   state the trade-off the table records (posting, granule size).
2. Choose the version family from the family holdings in the same
   concept: the family whose holdings cover the dates in play, with the
   orbit-phase gotcha read first whenever the range touches 2023.
3. Resolve the ShortName and concept id from that table; never type one
   from memory, and never plan against an umbrella collection.
4. Search with earthaccess (`search_data(short_name=..., temporal=...,
   bounding_box=...)`): granules are whole passes, so a regional search
   returns every pass that touches the box, and the load trims to the
   region before any aggregation.
5. Record the processing baseline (`crid`) of every granule actually
   loaded; the dataset concept's Known issues say why a subset's
   consistency claims depend on that record.
6. Decode the bit-packed quality flags before any statistic (the
   quality-control rules), apply the crossover correction the gotcha
   prescribes with its gate, keep the two swaths and the nadir gap
   intact, and quote the uncertainty variables the concept's Uncertainty
   section names.
