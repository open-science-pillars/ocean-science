---
type: dataset-gotcha
title: "The MASS-suffixed velocities are already mass-weighted: multiplying by hFac double-counts"
description: "UVELMASS and VVELMASS already include the hFac open-fraction weighting; a section transport that multiplies them by hFac again is silently biased low, and the official helper uses UVELMASS times drF times dyG with no hFac."
tags: [ecco, transport, hfac, velmass, native-grid]
severity: high
dataset: ../datasets/ecco-v4r4.md
eval_case: ecco-velmass-double-count
# eval id reserved for the eval-commons seed.
generated: { by: claude-code/fable-5, at: 2026-09-01T05:11:19Z }
verified: { by: human:PaulMRamirez, at: 2026-09-01T05:53:24Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: ecco-skills-eval
    resource: https://github.com/podaac/ecco-skills/blob/main/docs/eval1.md
    title: "podaac/ecco-skills evaluation round 1: section transport double-counted hFac with UVELMASS; fixed to match the official calc_section_vol_trsp"
  - id: volume-flux-family
    resource: ../fields/ecco-v4r4/volume-flux-3d.md
    title: "The fields concept for the mass-weighted volume flux family, where the MASS-suffixed variables live"
  - id: tutorial-mht
    resource: ../tutorial/ecco-mht-tutorial-example.md
    title: "Tutorial companion for the MHT chapter, whose section machinery uses the mass-weighted variables"
---

# The MASS-suffixed velocities are already mass-weighted

UVELMASS and VVELMASS carry the hFac open-fraction weighting inside
the variable; that is what the MASS suffix means.[^volume-flux-family]
A section transport assembled as UVELMASS times hFacW times drF times
dyG therefore applies the partial-cell weighting twice and is silently
biased low wherever partial cells exist, which is most of the ocean
floor and every coastline. The official helper computes volume
transport as UVELMASS times drF times dyG, with no hFac and no bolus
term for volume.[^tutorial-mht]

An independent PO.DAAC skills project shipped exactly this
double-count in its first section-transport draft; an adversarial
evaluation caught it and the fix was verified against the official
helper.[^ecco-skills-eval] The rule that travels: before weighting any
ECCO variable, read whether the weighting is already inside it, and
the MASS suffix says it is.

[^ecco-skills-eval]: podaac/ecco-skills eval round 1, the caught double-count
[^volume-flux-family]: fields/ecco-v4r4/volume-flux-3d.md
[^tutorial-mht]: tutorial/ecco-mht-tutorial-example.md
