---
type: recipe
title: "Closed volume budget on the ECCO v4r4 native grid"
description: "The z* volume budget closes pointwise to round-off on transport convergence ALONE; the surface freshwater flux is already carried in WVELMASS, so adding it as a forcing term double-counts."
tags: [ecco, volume-budget, native-grid, closure, llc90, freshwater]
timestamp: 2026-07-05
inputs: "ECCO v4r4 native-grid collections: ETAN snapshots (SSH snapshot) for the z* tendency, 3D volume fluxes (UVELMASS, VVELMASS, WVELMASS), and geometry; monthly volume fluxes bracketed by month-boundary ETAN snapshots"
expected: "Pointwise ABSOLUTE residual on interior wet cells (2010, tile 1, 3.34M cell-months, measured 2026-07-05): max 4.6e-12 1/s, p99.9 5.4e-13, median 1.8e-14; the budget closes to float32 round-off"
expected_uncertainty: "Tolerance is ABSOLUTE (float32 quantization floor). Golden asserts max <= 1e-11 1/s and p99.9 <= 1e-12 (about 2x measured). The critical formulation check: with a separate oceFWflx forcing term added, the surface-layer residual jumps to order 1e-8 (six orders above round-off); the closure is the detector for that double-count"
evidence:
  - https://github.com/open-science-pillars/ocean-science/blob/main/skills/ecco/references/budget-formulation.md
  - ../gotchas/ecco-native-vs-regridded.md
status: verified
verified: 2026-07-05
verified_by: OSP steward review
---

# Closed volume budget on the ECCO v4r4 native grid

**Method.** The z* volume budget has the tracer set to 1:

1. **Tendency**: `d(s*)/dt` from month-boundary ETAN snapshots
   (`s* = 1 + ETAN/Depth`), the same fractional volume change for every
   layer in a column.
2. **Advective convergence** of the mass-weighted volume transports:
   `UVELMASS * dyG * drF` (west faces), `VVELMASS * dxG * drF` (south
   faces), and `WVELMASS * rA` (vertical faces), divided by the
   partial-cell volume `rA * drF * hFacC`.

There is **no separate forcing term.** `WVELMASS` at the surface already
carries the freshwater volume flux (P minus E plus runoff), so the
budget closes on transport convergence alone.

**The double-count trap (measured 2026-07-05).** Adding `oceFWflx` as a
surface forcing term (by analogy with the heat budget's forcing) drives
the surface-layer residual to order 1e-8 1/s, six orders above the
round-off the rest of the column achieves; the entire error sits at
k = 0. The correct budget has no FW forcing, and the closure detects the
mistake.

**Anchor (measured 2026-07-05, ECCO v4r4 2010, tile 1 interior).** The
expected values above; the budget closes to float32 round-off.

**Provenance.** Reproducible from the native-grid collections named in
`inputs`; the volume_budget golden asserts the measured tolerance
pointwise. Regridded inputs are refused
([ecco-native-vs-regridded](../gotchas/ecco-native-vs-regridded.md)).
