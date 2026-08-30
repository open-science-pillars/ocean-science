# ECCO v4r4 variable catalog (llc90 native grid)

Reference for the ecco skill, per SPEC §4.2.

**Single source (knowledge-vs-skills doctrine, deduplicated
2026-08-30):** the collection families, ShortNames, and per-variable
rows that lived in this file now live in the knowledge bundle's fields
layer, one Data Collection concept per family, granule-verified and
steward-signed. Consult the bundle by path before loading:

- Family index: `knowledge/fields/ecco-v4r4/index.md` (26 families
  covering all 90 ECCO_L4_*V4R4* collections; the ten demo-critical
  families are authored and stable as of 2026-08-30, the rest arrive
  via the community lane).
- Per-family concepts: `knowledge/fields/ecco-v4r4/<family>.md`
  (geometry, temp-salinity, ocean-vel, volume-flux-3d,
  temperature-flux-3d, salinity-flux-3d, heat-flux, fresh-flux, ssh,
  obp, and the rest as they land). Each carries the ShortName variants,
  a Schema table with units and grid placement, per-row provenance, and
  Known-issues links to the constraining gotchas.

ShortName verification is owned by that layer: the family manifest and
`tools/verify_cmr.py` in the canonical repo (nasa-daac-knowledge)
re-verify every name against live CMR (last full sweep 2026-08-30,
90/90 reconciled clean), and machine confirmation is recorded as
process events on the concepts themselves. No table in this file is
authoritative for any ShortName or variable name; the bundle is.

## Load behavior (the procedure this file still owns)

- Grid geometry loads first, always, and merges into every native-grid
  dataset before analysis (`xarray.merge` with the data granules); the
  geometry family concept carries the variable inventory.
- Budget work consults the family concepts named by the recipe in play
  (the recipe concepts in `knowledge/recipes/` name their input
  collections) and the gotchas its Known-issues links reach.

## Access pattern

`ecco_access.ecco_podaac_to_xrdataset(query, version='v4r4', StartDate=,
EndDate=, mode=)` accepts ShortNames or variable names for TIME-RANGED
collections (call pattern per the ECCO v4 Python tutorial).

**Static-collection quirk (observed 2026-07-04, ecco_access 0.3.1):**
given a static collection (GEOMETRY; likely MIX_COEFFS too) with no date
range, ecco_access synthesized a dated granule filename
(`GRID_1992-01-01_...`) that does not exist (archive 404) and estimated
a 75.8 GB download for a single-granule collection. Fetch static
collections via `earthaccess.search_data(short_name=...)` plus
`earthaccess.download` instead: granule names come from CMR, never
guessed. Grid geometry then merges via `xarray.merge` with the data
granules.
