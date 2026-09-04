---
name: ecco
description: "ECCO v4r4 ocean state estimate: LLC90 native grid, PO.DAAC collections through the fields concepts, budget formulation, dynamical consistency. Knowledge first."
user-invocable: false
---

# ecco

Background expertise for the ECCO v4r4 ocean state estimate. This
skill carries the pointer, not the facts: the grid, the collections,
the formulation, and every caveat live in the knowledge bundle's
concepts (the pinned PO.DAAC copies under `knowledge/snapshot-podaac/`,
declared in `knowledge/snapshot.yaml`), and the three reference
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
`knowledge/snapshot-podaac/`:

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
- the recipes, attested computations, validity domains, and findings
  under `recipes/`, `computations/`, `validity-domains/`, and
  `findings/` by the `ecco-` prefix; an attested computation owns its
  pass bar and its sanctioned code, reached through the concept.

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
  convention `knowledge/snapshot-podaac/conventions/ecco-budget-formulation.md`,
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
`knowledge/snapshot-podaac/connectors/earthdata-mcp.md` (a draft, voiced
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
