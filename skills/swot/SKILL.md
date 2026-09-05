---
name: swot
description: "SWOT KaRIn L2 SSH: product tiers, orbit phases (1-day cal/val vs 21-day science), two-swath geometry, cycle/pass naming, earthaccess."
user-invocable: false
---

# swot

Background expertise for SWOT KaRIn sea surface height work. This
skill carries the pointer, not the facts: the product inventory,
granule anatomy, orbit phases, and current baseline live in the
knowledge bundle's concepts, and `references/swot-products.md` is the
procedure for choosing among them; this file says when to reach for
which, and carries no dataset facts, numbers, or gotcha rules of its
own.

## Knowledge first

Before ANY SWOT analysis, consult installed knowledge concepts first,
as the core `consult-knowledge` skill sets out (the directories to
glob, how to voice a concept's status, which concept wins on conflict),
by the products, variables, tiers, cycles, and dates in play (search
terms: swot, karin, ssha, a tier name, cycle, pass, crid, crossover,
cal/val). Read each match, restate what it changes about the plan
before computing, and cite it by path. A concept added since you last
ran is found this way, not from this file. The concepts this plugin
resolves to today, all under `knowledge/podaac/`:

- the dataset concept `datasets/swot-karin.md`: identity and swath
  geometry, granule structure, the Variants table (tiers by version
  family with ShortNames and concept ids), the family holdings, the
  nadir altimeter collections, the uncertainty variables and what they
  do not cover, and the known issues (baseline drift within
  collections, the whole-pass spatial-search caveat);
- `gotchas/swot-calval-orbit-phases.md`: the two orbit phases, the
  cycle numbering, and the version-family trap;
- `gotchas/swot-crossover-unapplied.md`: the crossover correction that
  arrives unapplied, the field that carries it, and its quality gate.

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
are dataset facts: read them from the dataset concept, not from here.

## Choosing a tier and a family

Pick the tier from the dataset concept's Variants table
(`knowledge/podaac/datasets/swot-karin.md`) by what the
analysis needs: SSH-anomaly work, the full correction and uncertainty
variable set, wind and wave state, or the finest-scale structure. The
tier inventory, its trade-offs (posting, granule size), the ShortNames
and concept ids per version family, and the family holdings live in
that concept; `references/swot-products.md` is the procedure for
reading them. The version family in play follows the holdings and the
dataset concept's current-baseline note, never a value hardcoded here.

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
are DEFERRED to the hydrology plugin; this plugin's SWOT scope is
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
