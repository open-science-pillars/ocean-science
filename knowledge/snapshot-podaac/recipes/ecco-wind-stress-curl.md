---
type: recipe
title: "Wind-stress curl and Ekman pumping on the native grid"
description: "The rotation-proof route to curl: compute in the tile-local frame where curl's rotation-invariance makes the trap structurally impossible, then validate Ekman pumping against the model's own vertical velocity."
tags: [ecco, wind-stress, curl, ekman, recipe, native-grid]
inputs: "ECCO_L4_STRESS_LLC0090GRID_MONTHLY_V4R4 (oceTAUX, oceTAUY); ECCO_L4_OCEAN_VEL_LLC0090GRID_MONTHLY_V4R4 (WVEL) for the same month; the geometry granule (dxC, dyC, Depth, YC, maskC)"
expected: "Month 2009-12 (measured 2026-09-01): Ekman pumping vs model WVEL at the 70 m interface, open-ocean interior, r = 0.8225 over 20,751 cells; median absolute curl 9.25E-08 N m-3"
expected_uncertainty: "The model's WVEL contains eddies, mixing, and topographic steering, not only Ekman pumping, so moderate correlation is the CORRECT outcome; near-perfect agreement would itself be suspect. Exclude the equatorial band (f near zero) and shelf seas (coastal upwelling is not wind-curl driven at grid scale)"
generated: { by: claude-code/fable-5, at: 2026-09-01T05:35:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-01T05:53:24Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: attested-computation
    resource: ../computations/ecco-wind-stress-curl.md
    title: "The attested computation this recipe walks: local-frame formulation, contract, reference run"
  - id: gradients-curl
    resource: ../tutorial/gradients-and-curl.md
    title: "Gradients and curl on the native grid"
---

# Wind-stress curl and Ekman pumping on the native grid

The historical failure mode for this calculation is rotating the
stress components for one purpose and then differencing them in a
frame they no longer match. The recipe's answer is structural: never
rotate. Curl is a rotation-invariant scalar, so computing d(tau_y)/dx
minus d(tau_x)/dy entirely in each tile's local frame, with the local
dxC and dyC metrics, gives the same field the geographic frame would,
and there is no second rotation to forget.[^gradients-curl] Average
the staggered stresses to cell centers first (oceTAUX lives on west
faces, oceTAUY on south faces).

Validation is against the model itself: Ekman pumping, one over rho0
times curl of tau over f, compared with WVEL at 70 m over the deep
open ocean between 10 and 55 degrees. Expect r near 0.82; expect it
NOT to be near 1, because the model's vertical velocity contains far
more than Ekman dynamics, and the attested form refuses any receipt
that drops that caveat.[^attested-computation]

[^attested-computation]: computations/ecco-wind-stress-curl.md, contract and reference run
[^gradients-curl]: tutorial/gradients-and-curl.md
