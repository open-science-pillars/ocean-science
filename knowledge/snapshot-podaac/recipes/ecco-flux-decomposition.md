---
type: recipe
title: "Splitting a flux into mean and eddy parts without an argument"
description: "Reynolds decomposition where the grouping is disclosed rather than debated: declare the mean window, verify the cross terms vanish, report the view you need, and ship all four terms so any reader can re-group."
tags: [ecco, flux-decomposition, reynolds, eddy, recipe, native-grid]
inputs: "ECCO_L4_OCEAN_3D_VOLUME_FLUX (VVELMASS); ECCO_L4_TEMP_SALINITY monthly (THETA); the geometry granule (dxG, drF, hFacC)"
expected: "southeast-atlantic-upper interior faces, year 2010 (measured 2026-09-01): mean-advective +9.04354 PW, eddy -0.06963 PW, total +8.97391 PW; identity residual 1.1e-16 relative, cross-term means 3.6e-17"
expected_uncertainty: "The four-term identity holds for ANY split point, so it proves algebra, not correctness; the oracle with teeth is the vanishing of the cross-term time means, which fails for any mean not taken over the declared window. Groupings change the view, never the numbers: a result reported in one grouping is comparable to another only through the four stored terms, which is why all four must travel"
generated: { by: claude-code/fable-5, at: 2026-09-01T15:40:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-01T15:55:00Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: attested-computation
    resource: ../computations/ecco-flux-decomposition.md
    title: "The attested computation this recipe walks: oracles, view-consistency rule, reference numbers"
---

# Splitting a flux into mean and eddy parts without an argument

The perennial argument about Reynolds decompositions (three terms or
four, which mean, which window) is a reporting question wearing a
correctness costume. Separate them. Correctness is two checks: the
four terms recompose the total at round-off, and the cross terms'
time means vanish, the second being the real test because it fails
for any overbar that is not the true mean of the declared
window.[^attested-computation]

Reporting is then a declared convention: full four-term, mean-plus-
eddy, or anomaly, disclosed in the receipt beside all four stored
terms, so two studies using different conventions reconcile through
the same stored numbers instead of arguing past each other. Weight
the mass-weighted velocity with face length times layer thickness and
nothing else, and state plainly whether the faces span a basin or the
inside of a box.[^attested-computation]

[^attested-computation]: computations/ecco-flux-decomposition.md
