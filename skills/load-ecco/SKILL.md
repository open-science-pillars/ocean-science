---
name: load-ecco
description: Load ECCO v4r4 data from PO.DAAC with grid auto-merge and Dask; volume confirmation gate; restates applicable gotchas.
---

# load-ecco

Bring ECCO v4r4 into the session safely: exact ShortNames, geometry
merged, gated on volume, gotchas restated. Works by slash command or conversationally
("load ECCO temperature for 2010").

## Behavior, in order

1. **Parse and show back:** variables or collections (resolved to EXACT
   ShortNames via the variable catalog; bare variable-name queries open
   an interactive picker that hangs scripted use), time range,
   time resolution (monthly, daily, snapshot), release (V4R4; the
   V4R4B rows for SSH and OBP per the catalog's Variants section).
2. **Knowledge first, restated:** the ecco-v4r4 dataset concept (no
   formal error fields; what stands in); native-vs-regridded when the
   request or downstream intent touches budgets or transports; the
   release note when SSH or OBP is involved; snapshots-not-monthly-means
   when the intent is a budget tendency.
3. **Search before fetching:** granule count and estimated volume
   BEFORE any download, via the time-ranged ecco_access path for dated
   collections and earthaccess directly for statics (geometry, mixing
   coefficients), per the catalog's access-pattern quirks.
4. **The volume gate.** Threshold from the project local config
   (template default 2 GB). At or below: state count, size,
   destination, proceed. Above: STOP, present count, total size,
   destination, and a smaller alternative (shorter window, monthly
   instead of daily, fewer collections), and wait for explicit
   confirmation. 3D flux and daily collections deserve a size estimate
   even under threshold.
5. **Load with the grid merged:** geometry granule
   (ECCO_L4_GEOMETRY_LLC0090GRID_V4R4) fetched or reused from cache and
   merged into the dataset (xarray merge); open with Dask chunks for 3D
   fields; hFac and MASS-variable semantics per the llc90 reference
   (never re-applied).
6. **Summary as provenance:** collections and granule counts loaded,
   time span, dims (time, tile, k, j, i), chunking, grid variables now
   present, cache location, and the concepts consulted. State the
   compute scale for what comes next (a year of monthly 3D is medium;
   decades of daily is large).

## Must NOT

- Never download above the gate threshold without explicit
  confirmation, on any surface.
- Never query ecco_access with bare variable names or fetch statics
  through it (catalog access-pattern quirks, observed 2026-07-04).
- Never deliver native-grid data without the geometry merged.
- Never mix V4R4 and V4R4B collections in one load without saying so.
- Never load monthly means when the stated purpose needs snapshots.
