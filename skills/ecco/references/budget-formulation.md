# ECCO v4r4 budget formulation: where it lives and how to apply it

Reference for the ecco skill. This file is procedure and pointers; the
formulation itself is a signed knowledge concept and is read from
there, never from here.

## The authority

- Terms, constants, sign conventions, discretization, and the
  formulation traps table:
  `knowledge/snapshot-podaac/conventions/ecco-budget-formulation.md`
  (the pinned copy of the PO.DAAC bundle's convention, verified
  against the ECCO v4 Python tutorial notebooks and carried verbatim
  by the sanctioned heat budget code).
- Pass bars and measured residuals, per budget:
  `knowledge/snapshot-podaac/computations/ecco-heat-budget.md` (the
  attested heat budget owns the heat tolerance and its baseline),
  `knowledge/snapshot-podaac/recipes/ecco-salt-budget.md` and
  `knowledge/snapshot-podaac/recipes/ecco-volume-budget.md` (the salt
  and volume residuals, and the oceFWflx double-count measurement).
- Sanctioned code and its attester:
  `knowledge/snapshot-podaac/references/computations/ecco_heat_budget.py`
  and `knowledge/snapshot-podaac/references/attesters/budget_residual.py`,
  reached through the heat computation concept.
- The gotchas a budget run must honor first:
  `knowledge/snapshot-podaac/gotchas/ecco-native-vs-regridded.md`
  (budgets close only on the native llc90 grid),
  `knowledge/snapshot-podaac/gotchas/ecco-geothermal-flux.md` (the
  geothermal input is not a PO.DAAC collection),
  `knowledge/snapshot-podaac/gotchas/ecco-velmass-hfac-double-count.md`
  (the MASS velocities and the flux variables already carry hFac).

## Procedure

1. Read the convention concept in full before writing a term. Quote
   its term definitions and constants in the plan; do not reconstruct
   them from memory or from another tutorial.
2. Take the pass bar from the owning computation or recipe, at the
   precision written there. Closure is judged pointwise, at every wet
   cell and every month, in absolute units; a relative-to-dominant-term
   ratio is not a closure criterion on a float32 archive.
3. Load month-boundary snapshots for the tendency and monthly means
   for the fluxes; merge the geometry collection for `rA`, `drF`,
   `hFacC`, `Depth`, `Z` and `Zp1`.
4. Compute the four terms exactly as the convention states them, with
   a tile-aware horizontal difference (or tile-interior cells only) and
   the bottom face zero-padded in the vertical.
5. Evaluate the residual against the bar. On failure, work the traps
   table in the convention concept from the residual's signature
   (where it acts: bottom cells, surface layer, tile seams, everywhere)
   to the omission that produces it, and cite the row. Regridded input
   is refused before any of this, not diagnosed after.
6. Cite every concept that shaped the run by path with its status; a
   draft is voiced as unverified.

The verification script `verification/ocean_budget.py` is the smoke
test over this procedure for heat: it stages the 2010 fixture, runs
the sanctioned computation from the pinned copy for a receipt, and
attests the receipt; the pass bar it asserts is the computation's, not
its own. The salt and volume scripts beside it still carry their
formulation inline until those computations reach stable.
