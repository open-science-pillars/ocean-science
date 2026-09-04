---
type: recipe
title: "Transport across a section of the ECCO v4r4 native grid"
description: "Sections as signed face masks from an indicator gradient: the topology that must be budget-verified before any flux crosses a seam, the per-collection weighting that flips between datasets, and the honesty rule for unanchored transports."
tags: [ecco, transport, section, seam, recipe, native-grid]
inputs: "ECCO_L4_OCEAN_3D_TEMPERATURE_FLUX (ADV*_TH, DF*_TH); ECCO_L4_OCEAN_3D_VOLUME_FLUX (UVELMASS, VVELMASS); the geometry granule (dyG, dxG, drF, YC, XC)"
expected: "global-26.5n, year 2010 (measured 2026-09-01): heat transport mean +1.0963 PW, agreeing with an independent implementation's 1.098 to 0.002 PW; volume mean -0.43 Sv. Seam calibration: 683,496 seam-adjacent cell months close at max 2.1e-11 degC per s, inside the interior budget tolerance"
expected_uncertainty: "Sections are masks, never index rows. Cross-tile ghost cells are mandatory: zeroing them turns every inside-bordering tile edge into spurious section faces (the recorded sabotage). Heat fluxes take no weighting, mass velocities take dyG or dxG times drF and no hFac; mixing those conventions is the recorded trap. A transport with no independent benchmark must say so; smooth transports make a one-row path error small, so check the receipt's mask digest and extent, not just its number"
generated: { by: claude-code/fable-5, at: 2026-09-01T15:20:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-04T20:45:44Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: attested-computation
    resource: ../computations/ecco-section-transport.md
    title: "The attested computation this recipe walks: topology verification, contract, reference runs"
  - id: meridional-transport-skill
    resource: https://github.com/open-science-pillars/ocean-science/blob/14a4eeab071d6f7d10f04e72c4878fef87c8b8de/skills/meridional-transport/SKILL.md
    title: "The meridional-transport skill doctrine: sections are masks, not index rows"
---

# Transport across a section of the ECCO v4r4 native grid

Build the section from an indicator, not from index rows: mark the
region on one side, difference the indicator across every stored
face, and the nonzero faces ARE the section, signed so positive
crosses into the region.[^meridional-transport-skill] On a tiled grid
that differencing must cross tile edges through the topology, and the
topology must be earned, not assumed: verify it geometrically, then
let the budget judge it, because a heat budget evaluated on
seam-adjacent cells with a wrong mapping cannot close at round-off.
Measured: all 24 edges close inside the interior
tolerance.[^attested-computation]

Then respect the two conventions that coexist in one calculation: the
tracer fluxes are already face-integrated transports (no weighting),
the mass velocities are not (face length times layer thickness, no
partial-cell factor). And keep the honesty rule: a transport across a
section with an independent benchmark gets anchored to it two-sided;
a transport without one is disclosure, not a validated claim, and its
receipt is required to say so.[^attested-computation]

[^attested-computation]: computations/ecco-section-transport.md
[^meridional-transport-skill]: ocean-science meridional-transport skill at the pinned commit
