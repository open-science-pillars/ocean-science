# ECCO v4r4 collections: how a request resolves

Reference for the ecco skill. This file is procedure and pointers; no
ShortName, variable name, or access rule is authoritative here.

**Single source:** the collection families, ShortNames, and
per-variable rows live in the knowledge bundle's fields layer, one
Data Collection concept per family, granule-verified and
steward-signed. Consult the bundle by path before loading:

- Family index: `knowledge/snapshot-podaac/fields/ecco-v4r4/index.md`
  (the families covering the ECCO_L4_*V4R4* collections, with each
  family's status).
- Per-family concepts: `knowledge/snapshot-podaac/fields/ecco-v4r4/<family>.md`
  (geometry, temp-salinity, ocean-vel, volume-flux-3d,
  temperature-flux-3d, salinity-flux-3d, heat-flux, fresh-flux, ssh,
  obp, and the rest the index lists). Each carries the ShortName
  variants, a Schema table with units and grid placement, per-row
  provenance, and Known-issues links to the constraining gotchas.

ShortName verification is owned by that layer: the family manifest and
the canonical repository's CMR verification tool re-verify every name
against live CMR, and machine confirmation is recorded as process
events on the concepts themselves. No table in this file is
authoritative for any ShortName or variable name; the bundle is. For
live cross-checks, the plugin's registered earthdata MCP connector
exposes the same catalog interactively (get_collections by short_name,
get_variables by collection concept id); signed Schema rows still come
only from the fields concepts and granule loads.

## Load behavior (the procedure this file still owns)

- Grid geometry loads first, always, and merges into every native-grid
  dataset before analysis (`xarray.merge` with the data granules); the
  geometry family concept carries the variable inventory.
- Budget work consults the family concepts named by the recipe in play
  (the recipe concepts in `knowledge/snapshot-podaac/recipes/` name their input
  collections) and the gotchas its Known-issues links reach.

## Access pattern

Time-ranged collections load by the access pattern the dataset concept
records (`knowledge/snapshot-podaac/datasets/ecco-v4r4.md`, Access:
ecco_access with exact ShortNames and a date range). Static
collections (geometry, and the others the gotcha names) do not: the
static-collection gotcha
`knowledge/snapshot-podaac/gotchas/ecco-access-static-collections.md`
records the failure and prescribes the earthaccess path, read from
there. Grid geometry then merges via `xarray.merge` with the data
granules.
