---
type: recipe
title: "Closed salt budget on the ECCO v4r4 native grid"
description: "The four-term salt budget (z* tendency, advective and diffusive convergence, surface salt flux plus the brine plume) closes pointwise to float32 round-off on the native llc90 grid."
tags: [ecco, salt-budget, native-grid, closure, llc90]
generated: { by: knowledge-seeder/claude, at: 2026-07-05T00:00:00Z }
inputs: "ECCO v4r4 native-grid collections: SALT snapshots (TEMP_SALINITY snapshot), 3D salinity fluxes (ADVx/y/r_SLT, DFxE/yE/rE_SLT, DFrI_SLT, oceSPtnd), surface salt flux SFLUX (FRESH_FLUX), ETAN snapshots (SSH snapshot), and geometry; monthly means bracketed by month-boundary snapshots for the tendency"
expected: "Pointwise ABSOLUTE residual on interior wet cells (2010, tile 1, 3.34M cell-months, measured 2026-07-05): max 7.2e-11 g/kg/s, p99.9 1.06e-11, median 8.3e-13; the budget closes to float32 round-off"
expected_uncertainty: "Tolerance is ABSOLUTE, not relative to the dominant term: on a float32 archive the quantization floor makes relative ratios meaningless (the same reason the heat-budget recipe re-grounded its tolerance). Golden asserts max <= 1.5e-10 g/kg/s and p99.9 <= 2e-11 (about 2x the measured values)"
sources:
  - id: budget-formulation
    resource: ../conventions/ecco-budget-formulation.md
    title: "Bundle convention: ECCO v4r4 budget formulation on the native grid"
  - id: ecco-native-vs-regridded
    resource: ../gotchas/ecco-native-vs-regridded.md
    title: "Bundle gotcha: ECCO budgets and transports close only on the native llc90 grid"
status: stable
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
stale_after: 2027-01-04
---

# Closed salt budget on the ECCO v4r4 native grid

**Method.** The same z* architecture as the heat budget, with salt
products and the salt-specific forcing:

1. **Tendency** with the z* scale factor: `s* * SALT` from month-boundary
   snapshots (`s* = 1 + ETAN/Depth`), differenced over the month.
2. **Advective convergence** of `ADVx_SLT`, `ADVy_SLT`, `ADVr_SLT`.
3. **Diffusive convergence** of `DFxE_SLT`, `DFyE_SLT`, and
   `DFrE_SLT + DFrI_SLT` (implicit vertical diffusion included).
4. **Forcing**: the surface salt flux `SFLUX` applied to the top layer
   plus the 3D brine-plume tendency `oceSPtnd`, divided by
   `RHOCONST * hFacC * drF`. No shortwave penetration and no geothermal
   term (those are heat-specific).

Divide each convergence by the partial-cell volume `rA * drF * hFacC`.
Closure: tendency equals the sum of the other three terms; the shared
architecture is the [budget formulation convention](../conventions/ecco-budget-formulation.md).[^budget-formulation]

**Anchor (measured 2026-07-05, ECCO v4r4 2010, tile 1 interior).** The
expected values above. The budget closes to float32 round-off, exactly
like the heat budget; a residual materially above 1e-10 g/kg/s signals a
formulation error (a dropped term, a double-applied hFac, or a
regridded input).

**Provenance.** Reproducible from the native-grid collections named in
`inputs`; the salt_budget golden asserts the measured tolerance
pointwise on interior wet cells (no tile-seam operators needed within a
tile). Regridded inputs are refused
([ecco-native-vs-regridded](../gotchas/ecco-native-vs-regridded.md)).[^ecco-native-vs-regridded]

[^budget-formulation]: Bundle convention: ECCO v4r4 budget formulation on the native grid
[^ecco-native-vs-regridded]: Bundle gotcha: ECCO budgets and transports close only on the native llc90 grid
