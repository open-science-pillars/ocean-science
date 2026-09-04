---
type: dataset-gotcha
title: "GRACE mascon coastal leakage: land signal bleeds into ocean mascons"
description: "Mascons straddling coastlines mix land hydrology and ice loss into nearshore ocean mass estimates; the CRI filter mitigates, never eliminates."
tags: [grace, leakage, coastal, mascons]
generated: { by: knowledge-seeder/claude, at: 2026-07-04T00:00:00Z }
severity: high
dataset: ../datasets/grace-fo-mascons.md
eval_case: grace-leakage
sources:
  - id: nasa-tellus-grac-grfo-mascon-cri-grid-rl06
    resource: https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4
    title: "PO.DAAC collection page: TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4"
  - id: grace-tellus
    resource: https://grace.jpl.nasa.gov/
    title: "GRACE Tellus project site (grace.jpl.nasa.gov)"
status: stable
verified: { by: human:PaulMRamirez, at: 2026-07-04T00:00:00Z }
stale_after: 2027-01-04
---

# GRACE mascon coastal leakage: land signal bleeds into ocean mascons

**Mechanism.** Mascons are 3-degree blocks; blocks straddling a
coastline integrate both land and ocean mass change. Strong land
signals (Greenland and glacier ice loss, large-basin hydrology)
therefore leak into adjacent ocean mascons, and vice versa. The CRI
(Coastline Resolution Improvement) filter in the standard gridded
product partitions straddling mascons between land and ocean using
independent information; it reduces leakage substantially but does not
eliminate it, and the 0.5-degree grid resolution overstates how
locally the answer is known.[^grace-tellus]

**Wrong-result mode.** Nearshore ocean mass series inherit land
signal: apparent coastal sea level or ocean-mass trends near Greenland,
Alaska, or major river basins can be dominated by leakage rather than
ocean change. Nothing errors; the series just is not what its
coordinates claim.

**Correct approach.** Nearshore mass analysis stays at mascon scale
(not grid-cell scale), uses the CRI product, keeps a buffer from
strong land sources or models them explicitly, and quotes the formal
uncertainty grids plus a leakage caveat for any mascon within one
block of the coast. Basin-scale open-ocean averages are robust; the
trap is specifically the nearshore.

**Verification.** The product landing page documents the CRI filter
and its purpose (link above)[^nasa-tellus-grac-grfo-mascon-cri-grid-rl06]; the leakage mechanism is intrinsic to
the mascon geometry (3-degree blocks vs coastline scales) and visible
by comparing CRI and non-CRI grids near Greenland for any month (both
collections verified live in CMR 2026-07-04).

[^nasa-tellus-grac-grfo-mascon-cri-grid-rl06]: PO.DAAC collection page: TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4
[^grace-tellus]: GRACE Tellus project site (grace.jpl.nasa.gov)
