---
type: Attested Computation
spheres: [hydrosphere]
title: "Reynolds flux decomposition from ECCO v4r4 (attested)"
description: "The meridional heat flux split about a declared time mean, with the grouping as a declared parameter rather than a settled question; two mathematical oracles, all four terms in every receipt regardless of grouping, and a view that cannot contradict the data."
tags: [ecco, flux-decomposition, reynolds, eddy, attested, native-grid]
runtime: python
parameters:
  - { name: region, type: "registered region name", required: true }
  - { name: grouping, type: "full-four-term, time-mean-eddy, or anomaly", required: true }
  - { name: year, type: "int, default 2010", required: false }
computation: skills/ocean-budget/scripts/ecco_flux_decomposition.py
executor:
  resource: skills/ocean-budget/scripts/ecco_flux_decomposition.py
  receipt: [run_id, code_sha256, data, bound_parameters, resolved_faces, results, mutation_evidence, caveats]
attester:
  resource: skills/ocean-budget/scripts/fluxdecomp_check.py
generated: { by: claude-code/fable-5, at: 2026-09-01T15:40:00Z }
verified:
  - { by: human:PaulMRamirez, at: 2026-09-04T02:40:20Z }
  - { by: human:PaulMRamirez, at: 2026-09-16T05:51:09Z, role: maintainer, source: https://github.com/open-science-pillars/nasa-daac-knowledge/pull/183 }
  - { by: human:PaulMRamirez, at: 2026-09-20T19:04:34Z, role: maintainer, source: https://github.com/open-science-pillars/ocean-science/pull/66 }
status: stable
stale_after: 2027-01-04
sources:
  - id: design-note
    resource: nasa-daac-knowledge/docs/regional-budget-design.md
    title: "The design note's flux-decomposition position: the grouping is a scope choice to disclose, not a correctness question to settle"
  - id: velmass-gotcha
    resource: knowledge/podaac/gotchas/ecco-velmass-hfac-double-count.md
    title: "The MASS-weighting gotcha the face aggregation applies: dxG times drF and no partial-cell factor"
---

# Reynolds flux decomposition from ECCO v4r4 (attested)

**Placement, 2026-09-20 (ADR E, a computation is a skill).** This
concept came from the nasa-daac-knowledge bundle at
`knowledge/podaac/computations/ecco-flux-decomposition.md`, and the
executor and the attester it names now ship in this package under
`skills/ocean-budget/scripts/`. The golden
`verification/ocean_budget.py` names every script it does. The executor
`skills/ocean-budget/scripts/ecco_flux_decomposition.py` is byte for
byte the file that was under the bundle, so its sha256 44084f528a3c4541
and every receipt that names it stand. The reference run
`flux-decomposition` reads the ECCO 2010 fixture cache, which this
environment does not hold, so it was not re-run here; the golden runs it
where the cache is present. The signature block is the one the
maintainer left; the concept sits at `status: draft` with no verified
event added, and the maintainer re-signs it after merge.

The meridional heat flux v times T through a registered region's
interior south faces, split about the declared time mean into
vbar Tbar, vbar T prime, v prime Tbar, and v prime T prime. Which
grouping a study should report is a scope choice, and this
computation deliberately does not settle it: the grouping travels as
a declared parameter, ALL FOUR stored terms travel in every receipt
regardless, and the attester fails any receipt whose reported view
disagrees with its stored terms, so no grouping can hide or reshape a
term.[^design-note]

**Two mathematical oracles, enforced before any receipt exists.** The
four-term identity must recompose the total at round-off, per face
per month; and the time means of the two cross terms must vanish at
round-off, which holds ONLY when the overbar is the true mean of the
declared window, so a stale or partial mean cannot pass. The identity
alone is algebra (it holds for any split point); the cross-term
oracle is the one with teeth, and both sabotages (a cross term
dropped, the mean taken over half the window) are rerun on every
execution and must be caught or no receipt is written. Velocity is
mass-weighted at the faces and aggregated with dxG times drF and no
partial-cell factor.[^velmass-gotcha]

**Reference run (2026-09-01, southeast-atlantic-upper, year 2010,
27,078 wet faces).** Identity 1.1e-16, cross-term means 3.6e-17;
mean-advective flux +9.04354 PW, eddy -0.06963 PW, total +8.97391 PW
northward through the region's interior faces (a within-box
decomposition, not a basin transport; the receipt says so). Attester
PASS on all three groupings of the same run; FAIL demonstrated on a
reported view doctored against the stored terms and on a stored term
deleted from the receipt.

**Data provenance.** The receipt also carries a `data` block: the data
root and the `RECORD.json` stamp the verify tool leaves in a tree it has
checked against its manifest (record name, manifest SHA-256,
verification time, report SHA-256). The attester refuses a receipt
whose `data.record` is not that stamp, so nothing is attested against a
tree this bundle has not manifested and verified. The two trees and
the rule are in docs/science-record.md.

[^design-note]: docs/regional-budget-design.md, the grouping-as-disclosure position
[^velmass-gotcha]: knowledge/podaac/gotchas/ecco-velmass-hfac-double-count.md
