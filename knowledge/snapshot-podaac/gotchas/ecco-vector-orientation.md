---
type: dataset-gotcha
title: "ECCO native velocities are grid-relative: UVEL and VVEL are not east and north"
description: "On the llc90 curvilinear tiles UVEL and VVEL point along model x and y; treating them as eastward and northward, or interpolating them component-wise like scalars, silently misdirects currents."
tags: [ecco, velocity, vectors, llc90, rotation]
generated: { by: claude-code/fable-5, at: 2026-08-30T21:05:00Z }
severity: high
dataset: ../datasets/ecco-v4r4.md
eval_case: ecco-vector-orientation
# eval case pending (eval-commons kit); id fixed here so the
# linter's dangling check closes when the case lands.
sources:
  - id: gh-151
    resource: https://github.com/ECCO-GROUP/ECCOv4-py/issues/151
    title: "ValueError using ecco_v4_py.vector_calc.UEVNfromUXVY"
  - id: gh-149
    resource: https://github.com/ECCO-GROUP/ECCOv4-py/issues/149
    title: "How to interpolate to the llcgrid from the regular lat-lon?"
  - id: gh-119
    resource: https://github.com/ECCO-GROUP/ECCOv4-py/issues/119
    title: "Doc missing for interpolating ECCO vectors to lat-lon grids?"
  - id: gh-9
    resource: https://github.com/ECCO-GROUP/ECCOv4-py/issues/9
    title: "Reorient/rotate tools"
  - id: fields-geometry
    resource: ../fields/ecco-v4r4/geometry.md
    title: "Bundle fields concept: grid geometry parameters (CS and SN granule-verified)"
  - id: fields-ocean-vel
    resource: ../fields/ecco-v4r4/ocean-vel.md
    title: "Bundle fields concept: ocean velocity"
status: draft
stale_after: 2027-01-04
---

# ECCO native velocities are grid-relative: UVEL and VVEL are not east and north

**Mechanism.** The llc90 grid is curvilinear: the tile-local x and y
axes rotate against geographic east and north across the domain. `UVEL`
and `VVEL` are the model x and y velocity components at the west and
south faces,[^fields-ocean-vel] and the geometry granule carries the
rotation angle cosine and sine `CS` and `SN` at cell centers for
converting between grid-relative and geographic
components.[^fields-geometry] The interpolated products distribute
east/north component variables instead (the EVEL*/NVEL* naming in the
interpolation documentation).[^gh-119]

**Wrong-result mode.** Treating `UVEL` as eastward and `VVEL` as
northward, or interpolating the native pair to a lat-lon grid component
by component as if they were scalars, misdirects currents wherever the
local axes are rotated; magnitudes stay plausible and nothing errors.
This is the largest recurring confusion in the community trackers
(27 lexicon hits in the 2026-08-30 ingest sweep): rotation-tool
failures and tooling requests,[^gh-151][^gh-9] and vector-specific
interpolation questions.[^gh-119][^gh-149]

**Correct approach.** Vector components are rotated to east/north with
the geometry's `CS` and `SN` before geographic interpretation or
comparison (the community tool is ecco_v4_py's
`UEVNfromUXVY`[^gh-151]), and interpolation of vectors happens after
rotation, never component-wise on the native pair. (Scalar versus
vector regridding discipline is workflow behavior owned by the
ocean-grids skill, which cites this concept.)

**Verification.** `CS` and `SN` are granule-verified in the geometry
fields concept;[^fields-geometry] the recurrence evidence is the cited
trackers. Drafted from the ingest-miner's 2026-08-30 sweep (cluster
llc-grid-orientation), completed for steward review.

[^gh-151]: ValueError using ecco_v4_py.vector_calc.UEVNfromUXVY
[^gh-149]: How to interpolate to the llcgrid from the regular lat-lon?
[^gh-119]: Doc missing for interpolating ECCO vectors to lat-lon grids?
[^gh-9]: Reorient/rotate tools
[^fields-geometry]: Bundle fields concept: grid geometry parameters (CS and SN granule-verified)
[^fields-ocean-vel]: Bundle fields concept: ocean velocity
