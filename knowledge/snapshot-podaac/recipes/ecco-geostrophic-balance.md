---
type: recipe
title: "Geostrophic velocity and thermal wind on the native grid"
description: "The full pressure potential (g ETAN plus PHIHYD), the density factor, and where a balance test has signal: the open-ocean interior validates at r 0.92, the shelf and the poles legitimately do not."
tags: [ecco, geostrophy, thermal-wind, recipe, native-grid]
inputs: "ECCO_L4_DENS_STRAT_PRESS_LLC0090GRID_MONTHLY_V4R4 (PHIHYD, RHOAnoma); ECCO_L4_SSH_LLC0090GRID_MONTHLY_V4R4 (ETAN); ECCO_L4_OCEAN_VEL_LLC0090GRID_MONTHLY_V4R4 (UVEL, VVEL) for the same month; the geometry granule (dxC, dyC, Depth, YC, Z, hFacC)"
expected: "Month 2009-12 at 351 m (measured 2026-09-01): r = 0.9242 against the model's currents over the open-ocean interior (10-55 deg, seafloor deeper than 3000 m, 20,771 cells); r = 0.7921 over the full 10-55 band; thermal wind identity 351 to 722 m r = 0.6102"
expected_uncertainty: "Two traps produce plausible wrong fields: PHIHYD without g ETAN (measured r -0.04) and a missing density factor. The balance test itself has domain limits: shelf and slope cells drag r from 0.92 to 0.79, and poleward of 55 degrees a centered-difference tracer-point scheme has no signal (r near 0); report those bands, do not validate on them. The tutorial's staggered helper reaches 0.998 where this scheme reads 0.92"
generated: { by: claude-code/fable-5, at: 2026-09-01T05:35:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-01T05:53:24Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: attested-computation
    resource: ../computations/ecco-geostrophic-balance.md
    title: "The attested computation this recipe walks: contract, disclosure fields, reference run"
  - id: tutorial-geostrophic
    resource: https://ecco-v4-python-tutorial.readthedocs.io/Geostrophic_balance.html
    title: "ECCO v4 tutorial, geostrophic balance"
---

# Geostrophic velocity and thermal wind on the native grid

Build the pressure first and build it whole: p equals rho0 times (g
times ETAN plus PHIHYD). Both halves matter. PHIHYD alone omits the
barotropic surface loading and produces velocities that correlate at
r = -0.04 with the model's own currents while looking perfectly
plausible on a map; the surface term alone is surface geostrophy.
Divide the gradients by the local density rho0 plus RHOAnoma times f,
never bare rho0.[^attested-computation]

Then validate where the test has signal. Centered differences at
tracer points in the tile-local frame reproduce the model's interior
currents at r = 0.92 in the deep open ocean between 10 and 55 degrees;
the same code reads 0.79 when shelf and slope cells are included and
near zero poleward of 55, and those are properties of the TEST, not
bugs to fix silently. Report all three bands. The thermal wind
identity (shear of geostrophic velocity against density gradients
between two depths) is a second, independent check that needs no
extra data.[^tutorial-geostrophic] The attested form makes the weaker
bands required receipt fields, so the flattering number cannot travel
alone.[^attested-computation]

[^attested-computation]: computations/ecco-geostrophic-balance.md, contract and measured bands
[^tutorial-geostrophic]: ECCO v4 tutorial geostrophic balance chapter
