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
   ShortNames through the fields concepts,
   `knowledge/snapshot-podaac/fields/ecco-v4r4/`, one per collection
   family; bare variable-name queries open an interactive picker that
   hangs scripted use), time range, time resolution (monthly, daily,
   snapshot), release (V4R4; the V4R4B variants of SSH and OBP per
   their family concepts and the release-mixing gotcha).
2. **Consult the bundle for this load first.** Consult installed
   knowledge concepts first, as the core `consult-knowledge` skill
   sets out, by product, variable, time resolution, and downstream
   intent; the ecco skill lists the concepts this plugin resolves to.
   Read the dataset concept for the products, the fields concept for
   each collection (ShortName variants, Schema, Known issues), and the
   gotchas the request or downstream intent triggers
   (native-vs-regridded for budgets and transports, the release caveat
   for SSH or OBP, snapshots-for-tendencies for budgets, the
   static-collection access quirk for geometry). Restate what applies
   and cite; do not carry these facts in this skill.
3. **Search before fetching:** granule count and estimated volume
   BEFORE any download, on the dated access path the dataset concept
   records, or the static path its access gotcha
   (`knowledge/snapshot-podaac/gotchas/ecco-access-static-collections.md`)
   prescribes for geometry and the other static collections. Discovery and availability
   checks may use the registered earthdata MCP connector, no login
   needed: get_collections with short_name first (keyword second) to
   resolve, get_granules to verify the window and region actually carry
   granules before any coverage claim; the download itself stays on
   earthaccess with Earthdata Login.
4. **The volume gate.** Threshold from the project local config
   (`ocean-science.local.md`, "maximum ungated download size"). At or
   below: state count, size,
   destination, proceed. Above: STOP, present count, total size,
   destination, and a smaller alternative (shorter window, monthly
   instead of daily, fewer collections), and wait for explicit
   confirmation. 3D flux and daily collections deserve a size estimate
   even under threshold.
5. **Load with the grid merged:** geometry granule
   (ECCO_L4_GEOMETRY_LLC0090GRID_V4R4) fetched or reused from cache and
   merged into the dataset (xarray merge); open with Dask chunks for 3D
   fields; hFac and MASS-variable semantics per the geometry family
   concept and the hFac double-count gotcha (never re-applied).
6. **Summary as provenance:** collections and granule counts loaded,
   time span, dims (time, tile, k, j, i), chunking, grid variables now
   present, cache location, and the concepts consulted. State the
   compute scale for what comes next (a year of monthly 3D is medium;
   decades of daily is large).

## Must NOT

- Never download above the gate threshold without explicit
  confirmation, on any surface. (Hard gate: fires without consulting
  anything.)
- Never deliver native-grid data without the geometry merged. (Load
  procedure.)
- Never promise data exists from a collection-level match alone:
  granule-level verification (get_granules or a CMR granule search)
  precedes any coverage claim, and nothing the connector returns
  bypasses the bundle's gotchas.
- Never restate a dataset rule this skill could consult: the access
  quirks (bare-name queries, statics path), the V4R4/V4R4B release
  caveat, and the snapshots-vs-monthly-means rule live in the fields
  concepts and the ecco gotchas, and are read from them per load.
