---
type: recipe
title: "Closing a heat budget over a region of ECCO v4r4"
description: "The control-volume budget done honestly: three independent collections, two bars because one certifies missing physics, sabotage as shipped evidence, and full disclosure of the water actually integrated."
tags: [ecco, heat-budget, regional, control-volume, recipe, native-grid]
inputs: "ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX (ADV*_TH, DF*_TH); ECCO_L4_HEAT_FLUX (TFLUX, oceQsw); TEMP_SALINITY and SSH SNAPSHOT collections bracketing the period; the geometry granule; geothermalFlux.bin from the tutorial distribution"
expected: "Reference volume (southeast Atlantic, upper 323 m, year 2010, measured 2026-09-01): residual per volume max 1.632e-14 degC per s against the 1e-10 bar; relative max 1.850e-07 against 1e-6; geothermal omission fails the relative bar at 1.4e-05 while passing the absolute bar"
expected_uncertainty: "Both bars are required: the absolute bar alone certifies a budget missing geothermal flux (measured 1.24e-12, inside 1e-10). The rim must be read from raw face fluxes on a path disjoint from any divergence field, or the closure test is circular. No oracle checks the mask is the region you meant: read the receipt's resolved extent before believing the number. Volumes within one tile interior only, until seam-calibrated sections land"
generated: { by: claude-code/fable-5, at: 2026-09-01T15:00:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-04T02:40:20Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: attested-computation
    resource: ../computations/ecco-regional-heat-budget.md
    title: "The attested computation this recipe walks: contract, mutation evidence, reference run"
  - id: design-note
    resource: ../../../docs/regional-budget-design.md
    title: "The design note: why two bars, why the disjoint rim path, what no oracle can check"
---

# Closing a heat budget over a region of ECCO v4r4

Assemble the three sides from three different collections: the
tendency from snapshots (with the free-surface scale factor from
bracketing ETAN), the boundary transport from the raw face fluxes at
the volume's rim and its top and bottom faces, and the forcing from
the surface fluxes with shortwave penetration, plus geothermal at
bottom wet cells. Independence is the point: if the rim extraction,
signs, or staggering are wrong, three collections cannot conspire to
agree.[^attested-computation]

Judge the closure against TWO bars. The absolute per-volume bar
inherits the pointwise tolerance; the relative bar exists because the
absolute one certifies a budget missing real physics (geothermal
omission measured inside it).[^design-note] Then read the disclosure
before quoting the number: the receipt states exactly which cells
were integrated (extent, counts, volume, mask digest), because a box
off by one cell or a swapped coordinate closes perfectly on the wrong
water, and no oracle exists that can catch it. The attested form
ships its own sabotage record: four mutations rerun on every
execution, each required to fail or to prove it could not matter
here.[^attested-computation]

[^attested-computation]: computations/ecco-regional-heat-budget.md
[^design-note]: docs/regional-budget-design.md
