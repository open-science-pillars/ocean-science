---
name: ecco
description: "ECCO v4r4 ocean state estimate: LLC90 native grid, variable catalog and PO.DAAC ShortNames, budget formulation, dynamical consistency. Knowledge first."
user-invocable: false
---

# ecco

Background expertise for the ECCO v4r4 ocean state estimate. This skill is deliberately
reference-heavy: the details live in three reference documents beside it,
and in the knowledge bundle's concepts; this file says when to reach for
which.

## Knowledge first

Before ANY ECCO analysis, DISCOVER and consult the installed knowledge
bundle, do not work from a remembered list of rules. Search
`knowledge/datasets/`, `knowledge/gotchas/`, and `knowledge/recipes/`
for every concept touching the products, quantities, and depth range in
play (glob and grep by product name, variable, and topic), read the
matches, and restate what each changes about the plan before computing,
citing it by path. A concept added since you last ran is found this way.
Expected numbers, uncertainty framing, release and version caveats, the
geothermal term, and the native-vs-regridded rule all live in concepts
and are read from them, never from this skill.

The one rule that fires WITHOUT consulting anything is the hard refusal
below: a budget or transport on regridded fields is refused outright.

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

- `references/llc90-grid.md`: any spatial operation. Tiles, C-grid
  staggering, partial cells (hFac), tile-seam differencing, the
  Pacific-sector rotation, why plotting needs resampling.
- `references/variable-catalog.md`: any data request. ShortNames
  verified against live CMR with the verification date recorded;
  velocity vs OBP disambiguation; snapshot collections for budget
  bookends; the V4R4B note; geothermal flux as ancillary input.
- `references/budget-formulation.md`: any budget. The four terms quoted
  from the ECCO v4 tutorial, constants, the z* tendency correction,
  shortwave penetration, geothermal at the bottom cell, and the traps
  table mapping residual signatures to formulation errors.

## Access pattern

Load grid geometry first (`ECCO_L4_GEOMETRY_LLC0090GRID_V4R4`, one
static granule) and merge it with every native dataset. Data access via
`ecco_access.ecco_podaac_to_xrdataset(query, version='v4r4',
StartDate=, EndDate=, mode=)`; open with Dask chunks for 3D fields
(a year of monthly THETA is medium compute; decades of 3D fluxes are
large). Volume-gated loading and gotcha restatement are the load-ecco
workflow's job; this skill supplies what it restates.

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
- Never invent numbers: expected values and uncertainty ranges come
  from the recipe concepts, cited.
