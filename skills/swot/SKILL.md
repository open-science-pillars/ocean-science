---
name: swot
description: "SWOT KaRIn L2 SSH: product tiers, orbit phases (1-day cal/val vs 21-day science), two-swath geometry, cycle/pass naming, earthaccess."
user-invocable: false
---

# swot

Background expertise for SWOT KaRIn sea surface height work. This skill is
deliberately reference-heavy: the product inventory, granule anatomy, and
orbit-phase details live in `references/swot-products.md` (CMR-verified
2026-07-04) and in the knowledge bundle's concepts; this file says when to
reach for which, and carries no dataset facts, numbers, or gotcha rules of
its own.

## Knowledge first

Before ANY SWOT analysis, DISCOVER and consult the installed knowledge
bundle; do not work from a remembered list of rules. Search
`knowledge/datasets/`, `knowledge/gotchas/`, and `knowledge/recipes/` for
every concept touching the products, variables, tiers, cycles, and dates in
play (glob and grep by product name, variable, and topic), read the matches,
restate what each changes about the plan before computing, and cite it by
path. A concept added since you last ran is found this way. The processing
baseline and version-family state, the ssha uncertainty variables and what
they do not cover, the crossover-calibration issue, the CRID drift, and the
orbit-phase/cal-val trap all live in concepts and are read from them, never
from this skill.

One consult fires first, always: any date range touching 2023 gets the
orbit-phase concept read BEFORE anything else, because a window spanning the
mid-2023 transition and an empty early-mission query are both silent
failures that concept explains.

## What KaRIn SSH is

Wide-swath interferometric altimetry: two SSH swaths separated by a nadir
gap, resolving two-dimensional SSH structure at scales conventional nadir
altimetry cannot. What makes it different to work with is the swath geometry
(cross-track systematic errors, signed cross-track coordinates, the gap),
phase-dependent sampling, and bit-packed quality flags that gate every
pixel. The swath widths, along-swath posting, per-tier posting, and gap size
are dataset facts: read them from the dataset concept and the products
reference, not from here.

## Choosing a tier

Pick the tier from the reference's table (`references/swot-products.md`) by
what the analysis needs: SSH-anomaly work, the full correction and
uncertainty variable set, wind and wave state, or the finest-scale
structure. The tier inventory and its trade-offs (including granule size)
live in that table; the version family in play is per the dataset concept's
current-baseline note, never hardcoded here.

## Working rules (procedure)

- **Flags gate pixels (method):** decode the bit-packed quality flags before
  any statistics (quality-control's decoding rules apply); report the
  fraction masked and why. Flag gating is necessary but not sufficient;
  whether an ssha field is analysis-ready before its corrections are applied
  is a dataset question, answered by the concepts the consult step surfaces.
- **Respect the swath structure (method):** summaries and grids are
  per-swath with the nadir gap intact; treat the two swaths as having
  independent error profiles; never interpolate across the gap (hard
  refusal, below).
- **Cycle/pass is the unit of acquisition (method):** regional work is a
  spatial search over whole passes, then a trim to the region before any
  aggregation (subset before you aggregate). What a "cycle" spans depends on
  the orbit phase, which is dataset knowledge: read the orbit-phase concept.
- **Uncertainty travels with the data (method):** quote the ssha uncertainty
  variables with results per the house uncertainty rule, with the caveats
  the dataset concept records (what the per-sample field does and does not
  cover).
- Loading is the load-swot workflow's job (volume gate, flag decode,
  swath-aware summary); this skill supplies what it restates.

## Hydrology

SWOT river, lake, and inundation products exist as separate collections and
are DEFERRED to the hydrology plugin (Phase 2); this plugin's SWOT scope is
KaRIn L2 SSH and the nadir altimeter products.

## Hard refusals (invariant, universal; fire without consulting anything)

- Never interpolate across the nadir gap: it is a real data void, and
  interpolation fabricates SSH that was never measured.
- Never put unflagged pixels into statistics: pixels that have not passed
  flag gating are not data.
- Never hardcode a processing baseline, version family, or uncertainty
  caveat: read the dataset concept and record what the granules actually
  carry. Consulting the bundle is how a corrected or new concept changes
  this skill's behavior without editing it.

Dataset-specific rules (the cal/val-to-science orbit split, the empty-result
version-family trap, and the unapplied crossover calibration with its
`height_cor_xover` fix) are NOT restated here: they live in the swot gotcha
and dataset concepts and are surfaced by the consult step above. That
single-sourcing is what lets a corrected or new gotcha change this skill's
behavior without editing it.
