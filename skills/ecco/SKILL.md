---
name: ecco
description: "ECCO v4r4 ocean state estimate: LLC90 native grid, PO.DAAC collections through the fields concepts, budget formulation, dynamical consistency. Knowledge first."
user-invocable: false
---

# ecco

Background expertise for the ECCO v4r4 ocean state estimate. This
skill carries the pointer, not the facts: the grid, the collections,
the formulation, and every caveat live in the knowledge bundle's
concepts (the PO.DAAC bundle installed with the nasa-daac-knowledge
dependency, cited here as `knowledge/podaac/...`), and the three reference
documents beside this file are procedure over those concepts; this file
says when to reach for which.

## Knowledge first

Before ANY ECCO analysis, consult installed knowledge concepts first,
as the core `consult-knowledge` skill sets out (the directories to
glob, how to voice a concept's status, which concept wins on conflict),
by the products, quantities, and depth range in play (search terms: a
ShortName or family name, a variable, ecco, llc90, budget, transport,
release, snapshot, geothermal). Read each match, restate what it
changes about the plan before computing, and cite it by path. A
concept added since you last ran is found this way, not from this
file. The concepts this plugin resolves to today, all under
`knowledge/podaac/`:

- the dataset concept `datasets/ecco-v4r4.md`: what the state estimate
  is and is not, the native dims and tile layout, the access pattern,
  the no-formal-uncertainty framing, and its Known issues;
- the fields family `fields/ecco-v4r4/` (`index.md` and one concept
  per collection family): the ShortNames and their release variants,
  the Schema rows with units and grid placement, and the Known-issues
  links that reach each family's gotchas;
- the `ecco-` gotchas under `gotchas/`: native-vs-regridded, the
  geothermal input, the MASS and hFac double count, release mixing,
  the SSH inverse-barometer variants, the static-collection access
  quirk, the MXLDEPTH criterion, the native density EOS, the trend
  traps, and the rest the glob surfaces;
- the conventions `conventions/ecco-budget-formulation.md` and
  `conventions/consistency-versus-confrontation.md`;
- the recipes, validity domains, and findings under `recipes/`,
  `validity-domains/`, and `findings/` by the `ecco-` prefix.

The attested computations are not in that bundle. They live in this
package under `knowledge/computations/`, beside the scripts that run
them; an attested computation owns its pass bar and its sanctioned
code, reached through the concept.

The one rule that fires WITHOUT consulting anything is the hard refusal
below: a budget or transport on regridded fields is refused outright.
This skill owns that refusal for the plugin; ocean-grids, budget-closure,
and ocean-budget point here and keep their own method gates.

## What ECCO v4r4 is

A dynamically consistent ocean state estimate, 1992 to 2017: the MITgcm
run on the llc90 grid, fit to observations by adjusted controls
(initial conditions, forcing, mixing parameters), never by inserting
data increments. The payoff of that construction: model physics are
exactly satisfied, so property budgets close to machine precision and
transports are self-consistent. The cost: it is not an observation
product (comparisons against independent obs go through the compare-obs
workflow), its resolution (nominal 1 degree, 50 levels) does not resolve
eddies or shelf processes, and it carries no formal error fields.

## The three references, and when each applies

Each is procedure over the concepts it names; none carries a grid
fact, a ShortName, or a tolerance of its own.

- `references/llc90-grid.md`: any spatial operation. The order of
  operations for identifying the grid, merging geometry, the volume
  element, staggering, tile seams, vector rotation, plotting, and
  sections, with the concept each step reads.
- `references/variable-catalog.md`: any data request. How a request
  resolves to a collection through the fields concepts and loads, with
  the concepts that own ShortName verification and the access quirks.
- `references/budget-formulation.md`: any budget. The procedure, and
  the pointers to where the formulation lives: the four terms,
  constants, the z* tendency correction, shortwave penetration,
  geothermal at the bottom cell, and the traps table are the signed
  convention `knowledge/podaac/conventions/ecco-budget-formulation.md`,
  read from there.

## Access pattern

Load grid geometry first (`ECCO_L4_GEOMETRY_LLC0090GRID_V4R4`, one
static granule) and merge it with every native dataset. Data access via
`ecco_access.ecco_podaac_to_xrdataset(query, version='v4r4',
StartDate=, EndDate=, mode=)`; open with Dask chunks for 3D fields
(a year of monthly THETA is medium compute; decades of 3D fluxes are
large). Volume-gated loading and gotcha restatement are the load-ecco
workflow's job; this skill supplies what it restates.

**Discover, Verify, Access (the earthdata connector).** The plugin
registers NASA's Earthdata MCP server in `.mcp.json`; its tool surface
and boundaries are the connector concept
`knowledge/podaac/connectors/earthdata-mcp.md` (a draft, voiced
as such), read from there. The order is procedure: Discover with
get_keywords and get_collections (short_name resolution first, keyword
search second); Verify availability with get_granules for the exact
window and region BEFORE promising data exists; Access via earthaccess
with Earthdata Login, the only credentialed step. Two boundaries hold
whatever the concept's status: nothing the connector returns bypasses
a bundle gotcha (a discovered regridded collection is still refused for
budgets; SSH and OBP hits still carry the release discipline), and a
Schema row is trusted only from the signed fields concept or a granule
load, never from get_variables alone.

## Attested runs

The computations that validate the state estimate's own dynamics, its
global heat content and the one sanctioned trend method belong to no
single workflow skill; their scripts sit beside this one, so an agent
finds them the way it finds every other procedure. The workflow skills
wrap the rest (ocean-budget the budgets and the flux decomposition,
transport-analysis the sections and the overturning, compare-obs the
confrontations, sea-level-analysis the partition and the steric
height, sea-level-budget the budget closure).
The executor and the attester of every computation below ship in this
package, in the scripts directory of the skill that runs them, and the
concept each one answers to is under `knowledge/computations/`.
`${CLAUDE_PLUGIN_ROOT}` below is this package's root, which the runtime
sets. Never
edit an executor: its attester hashes it, and a changed hash fails by
construction. Run the named attester on the receipt before quoting any
number from it; a FAIL is reported as a FAIL with the failing field
named, never worked around. These executors take no `--runtime` flag
(their receipts carry no runtime block); record the runtime name
(`claude-code` here) in the report beside the receipt's run id.

Every executor here reads the native granules from `--data-root`
(default `~/ECCO_V4r4`): the 2010 fixture cache (about 2.5 GB, the
geometry granule plus the monthly and snapshot collections the concept
names, fetched with earthaccess under an Earthdata Login; the
repository's goldens tree stages it) or the science record over 1992
to 2017 (`~/ECCO_V4r4_record`). The tree must carry the RECORD.json
stamp the provider's verify tool leaves after checking it against its
manifest (`uv run <root>/tools/science_record_verify.py --manifest
${CLAUDE_PLUGIN_ROOT}/knowledge/references/retrieval/fixtures-2010-manifest.json --data-root
~/ECCO_V4r4 --checksum all --exact --stamp`, once after the first
fetch), since every attester refuses a receipt from an unstamped tree.

**Global ocean heat content, `ecco-ocean-heat-content`**
(`knowledge/computations/ecco-ocean-heat-content.md`; executor
`skills/ecco/scripts/ecco_ohc.py`, attester
`skills/ecco/scripts/ohc_check.py`). Binds `months` (one or more
`YYYY-MM`; the change is last minus first):

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ecco/scripts/ecco_ohc.py --months 2010-01 2010-12 \
  --data-root ~/ECCO_V4r4 --receipt /tmp/ohc-receipt.json
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ecco/scripts/ohc_check.py /tmp/ohc-receipt.json
```

The receipt carries `ohc_J_by_month`, `ohc_change_J`, the grid
anchors and the potential-temperature baseline caveat; the change
between months is the quantity, and the absolute value is never
quoted without the caveat. The Argo-based counterpart is this plugin's
own argo-ohc skill.

**Trend with an honest interval, `ecco-trend-ci`**
(`knowledge/computations/ecco-trend-ci.md`; executor
`skills/ecco/scripts/ecco_trend_ci.py`, attester
`skills/ecco/scripts/trend_ci_check.py`). Binds `source` (a
sanctioned receipt), `field` (a monthly `{YYYY-MM: value}` field in
it), `value_units`, and optionally `scale` (default 1.0),
`report_units` and `deseasonalize` (`climatology`, the default, needs
complete years; otherwise `none`):

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ecco/scripts/ecco_trend_ci.py \
  --source /tmp/ohc-receipt.json --field ohc_J_by_month \
  --value-units J --scale 1e-21 --report-units ZJ \
  --deseasonalize climatology --receipt /tmp/ohc-trend-receipt.json
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ecco/scripts/trend_ci_check.py /tmp/ohc-trend-receipt.json
```

The trend inherits the source receipt's run id, code hash and data
stamp; a series retyped into a bare file attests FAIL by
construction. The deseasonalized series a plot wants is the receipt's
`intermediates.series_fit`, drawn through the receipt-figures skill.

**Geostrophic balance and thermal wind, `ecco-geostrophic-balance`**
(`knowledge/computations/ecco-geostrophic-balance.md`;
executor `skills/ecco/scripts/ecco_geostrophy.py`, attester
`skills/ecco/scripts/geos_check.py`). Binds `month` (`YYYY-MM`),
`depth_m` (default 350) and `depth2_m` (default 700); `--fields PATH`
also writes the per-cell arrays for a map:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ecco/scripts/ecco_geostrophy.py --month 2009-12 \
  --depth-m 350 --depth2-m 700 --data-root ~/ECCO_V4r4 \
  --receipt /tmp/geos-receipt.json --fields /tmp/geos-fields.npz
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ecco/scripts/geos_check.py /tmp/geos-receipt.json
```

**Wind-stress curl and Ekman pumping, `ecco-wind-stress-curl`**
(`knowledge/computations/ecco-wind-stress-curl.md`; executor
`skills/ecco/scripts/ecco_curl_ekman.py`, attester
`skills/ecco/scripts/curl_check.py`). Binds `month` (`YYYY-MM`); the
WVEL interface stays at the contract's 70 m; `--fields PATH` for a
map:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ecco/scripts/ecco_curl_ekman.py --month 2009-12 \
  --data-root ~/ECCO_V4r4 --receipt /tmp/curl-receipt.json --fields /tmp/curl-fields.npz
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ecco/scripts/curl_check.py /tmp/curl-receipt.json
```

**Thermal-wind reconstruction from a level of no motion,
`ecco-thermal-wind-reconstruction`**
(`knowledge/computations/ecco-thermal-wind-reconstruction.md`;
executor `skills/ecco/scripts/ecco_thermal_wind_reconstruction.py`,
attester `skills/ecco/scripts/thermal_wind_check.py`). Binds `month`
(`YYYY-MM`), `reference_depth_m` (default 3000) and `map_depth_m`
(default 350); `--fields PATH` for a map:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ecco/scripts/ecco_thermal_wind_reconstruction.py --month 2009-12 \
  --reference-depth-m 3000 --map-depth-m 350 --data-root ~/ECCO_V4r4 \
  --receipt /tmp/thermal-wind-receipt.json --fields /tmp/thermal-wind-fields.npz
uv run ${CLAUDE_PLUGIN_ROOT}/skills/ecco/scripts/thermal_wind_check.py /tmp/thermal-wind-receipt.json
```

For all three dynamics checks the weaker bands (full band, polar, the
surface layer, below the reference level) are required receipt
fields and are reported beside the headline figure, never dropped;
the maps behind the scalars are drawn from the hashed fields file
through the receipt-figures skill and from nothing else.

## Must NOT

- Never compute budgets or transports on regridded ECCO fields; refuse
  and offer the native-grid path. (Hard refusal: invariant, universal,
  fires without consulting anything.)
- Never work from a remembered dataset rule where a concept exists:
  the geothermal term, the no-formal-uncertainty framing, the
  V4R4/V4R4B release caveat, snapshots-for-tendencies, and
  ECCO-is-a-state-estimate-not-observations all live in the bundle's
  concepts (datasets/ecco-v4r4.md and the ecco gotchas) and are read
  from them per analysis. Consulting them is how a new or corrected
  concept changes this skill's behavior without editing it.
- Never invent numbers: expected values, pass bars, and uncertainty
  ranges come from the recipe and computation concepts, cited.
- Never let a connector result bypass a bundle gotcha: discovery output
  is availability data, not permission; the native-grid refusal and
  release discipline apply unchanged to anything the MCP surfaced.
- Never treat get_variables output as a verified Schema: UMM variable
  records describe intent; signed fields concepts and granule loads are
  ground truth.
