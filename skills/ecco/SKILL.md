---
name: ecco
description: ECCO v4r4 ocean state estimate: LLC90 native grid, variable catalog and PO.DAAC ShortNames, budget formulation, dynamical consistency. Knowledge first.
user-invocable: false
---

# ecco

Background expertise for the ECCO v4r4 ocean state estimate. Authored in
Session 6 per SPECIFICATION.md v0.5.1 §4.2. This skill is deliberately
reference-heavy: the details live in three reference documents beside it,
and in the knowledge bundle's concepts; this file says when to reach for
which.

## Knowledge first

Before ANY ECCO analysis, consult the installed knowledge bundle and
restate what applies:

1. `knowledge/datasets/ecco-v4r4.md`: product identity, access, and the
   Uncertainty section (ECCO ships no formal error fields; what stands
   in for them and how to phrase it).
2. `knowledge/gotchas/ecco-native-vs-regridded.md`: budgets and
   transports are native-grid work; the interpolated 0.5 degree product
   is for display and comparison only. A regridded-budget request is
   REFUSED with this concept cited and the native path offered.
3. `knowledge/gotchas/ecco-geothermal-flux.md`: deep and full-depth heat
   budgets include the geothermal term or fail closure.
4. `knowledge/recipes/`: expected values and expected-uncertainty ranges
   for validated analyses (meridional heat transport, budget residuals).
   Skills read expected numbers from recipes, never from memory.

Restating means telling the user which concepts apply and what they
change about the plan, before computing.

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
  and offer the native-grid path (gotcha 2 above).
- Never omit geothermal flux from deep or full-depth heat budgets.
- Never invent error bars: ECCO has no formal uncertainty fields; state
  dynamical consistency plainly and use recipe expected-uncertainty
  ranges for validated quantities.
- Never mix V4R4 and V4R4B releases in one analysis without saying so.
- Never treat monthly means as budget bookends; tendencies come from
  snapshots.
- Never present ECCO as observations; it is a state estimate.
