---
type: recipe
title: "Global ocean heat content and its change from ECCO v4r4"
description: "Volume-weighted OHC on the native grid: the weighting that matters, the baseline that makes absolutes meaningless, and measured anchors a correct run reproduces."
tags: [ecco, ocean-heat-content, recipe, native-grid]
inputs: "ECCO_L4_TEMP_SALINITY_LLC0090GRID_MONTHLY_V4R4 (THETA) for the chosen months; the geometry granule (rA, drF, hFacC, maskC)"
expected: "Grid anchors any correct run reproduces: ocean surface area 3.5801E+08 km2 (tutorial publishes 3.58E+08), ocean volume 1.3350E+18 m3, 2,406,992 wet cells. Reference months (measured 2026-09-01): volume-mean THETA 3.6085 degC (2010-01), 3.6068 degC (2010-12); OHC change 2010-01 to 2010-12 = -9.485E+21 J"
expected_uncertainty: "Absolute OHC is baseline-relative (potential temperature vs 0 degC) and not physically meaningful alone; report changes. Volume-mean THETA outside 2 to 6 degC is suspect (provisional band). Two documented approximations bound interpretation: the fixed-volume weighting omits the z-star free-surface volume term, and monthly means alias sub-monthly variability relative to snapshots"
generated: { by: claude-code/fable-5, at: 2026-09-01T05:11:19Z }
verified: { by: human:PaulMRamirez, at: 2026-09-01T05:53:24Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: attested-computation
    resource: ../computations/ecco-ocean-heat-content.md
    title: "The attested computation this recipe walks: sanctioned code, receipt, attester, measured anchors"
  - id: tutorial-scalar
    resource: https://ecco-v4-python-tutorial.readthedocs.io/ECCO_v4_Example_calculations_with_scalar_quantities.html
    title: "ECCO v4 tutorial, scalar quantities: the area anchor and the volume-weighting pattern"
  - id: ecco-skills-caveats
    resource: https://github.com/podaac/ecco-skills
    title: "podaac/ecco-skills OHC skill: documents the z-star volume-term and snapshot-aliasing caveats this recipe carries"
---

# Global ocean heat content and its change from ECCO v4r4

The simplest whole-ocean scalar, and the weighting is the entire
trick: each cell's ocean volume is rA times drF times hFacC, area
times layer thickness times wet fraction, with hFacC handling partial
bottom cells and doubling as the land mask.[^tutorial-scalar] Sum
THETA against that volume, multiply by rhoConst and Cp, and report the
CHANGE between months, never the absolute, because potential
temperature makes the absolute number baseline-relative.[^attested-computation]

A correct run reproduces the grid anchors above exactly (they depend
only on the geometry granule) and lands volume-mean THETA near 3.6
degC for the 2010s.[^attested-computation] Two approximations are
carried, not hidden: the weighting holds cell volumes fixed, omitting
the z-star free-surface volume term, and monthly means alias
sub-monthly variability that snapshot differencing would
resolve.[^ecco-skills-caveats] The sanctioned, receipt-producing form
of this recipe is the attested computation beside it; a run of that
code can be attested by anyone from the receipt alone.

[^attested-computation]: computations/ecco-ocean-heat-content.md, the contract, anchors, and reference run
[^tutorial-scalar]: ECCO v4 tutorial scalar-quantities chapter
[^ecco-skills-caveats]: podaac/ecco-skills compute-ocean-heat-content documentation, the two stated caveats
