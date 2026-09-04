---
type: Attested Computation
title: "Geostrophic balance and thermal wind from ECCO v4r4 (attested)"
description: "Sanctioned geostrophic velocity from the full pressure potential (g ETAN plus PHIHYD), validated against the model's own currents; the weaker full-band and polar figures are REQUIRED receipt fields, so a receipt quoting only the favorable interior correlation fails attestation."
tags: [ecco, geostrophy, thermal-wind, attested, native-grid]
runtime: python
parameters:
  - { name: month, type: "YYYY-MM string", required: true }
  - { name: depth_m, type: "target depth, default 350", required: false }
  - { name: depth2_m, type: "second depth for thermal wind, default 700", required: false }
computation: references/computations/ecco_geostrophy.py
executor:
  resource: references/computations/ecco_geostrophy.py
  receipt: [run_id, code_sha256, data, bound_parameters, geostrophic, thermal_wind]
attester:
  resource: references/attesters/geos_check.py
generated: { by: claude-code/fable-5, at: 2026-09-01T05:35:00Z }
verified: { by: human:PaulMRamirez, at: 2026-09-04T02:58:02Z }
status: stable
stale_after: 2027-01-04
sources:
  - id: tutorial-geostrophic
    resource: https://ecco-v4-python-tutorial.readthedocs.io/Geostrophic_balance.html
    title: "ECCO v4 tutorial, geostrophic balance: the reference formulation and the geos_vel_compute helper"
  - id: density-factor
    resource: ../gotchas/ecco-geostrophic-density-factor.md
    title: "The density-factor gotcha this computation applies: divide by rho0 plus RHOAnoma, not rho0"
  - id: phihyd-surface
    resource: ../gotchas/ecco-phihyd-surface-pressure.md
    title: "The surface-pressure gotcha this computation's own first run produced: PHIHYD alone correlates near zero"
  - id: ecco-skills-corroboration
    resource: https://github.com/podaac/ecco-skills
    title: "podaac/ecco-skills geostrophic-velocity acceptance record: reproduces the tutorial helper to 1e-9 and the model's interior currents at correlation 0.998"
---

# Geostrophic balance and thermal wind from ECCO v4r4 (attested)

Geostrophic velocity at depth from u_g equals minus one over rho f
times dp/dy and v_g equals plus one over rho f times dp/dx, with the
pressure p as rho0 times the FULL potential, g times ETAN plus PHIHYD
(the surface loading is not in PHIHYD, and omitting it is the trap the
surface-pressure gotcha records),[^phihyd-surface] and the density as
rho0 plus RHOAnoma per the density-factor
gotcha.[^density-factor] Gradients are centered differences at tracer
points in each tile's local frame; the balance relation holds in any
right-handed local frame, so no rotation is needed. Validation is
against the model's own UVEL and VVEL averaged to tracer points, plus
the thermal wind identity between the two depths.

**Attestation contract.** A run passes only when the receipt's
code_sha256 matches the sanctioned computation, the bound parameters
are exactly the contract set, and ALL THREE validation figures are
present: the open-ocean interior correlation (10 to 55 degrees,
seafloor deeper than 3000 m), the full 10 to 55 band including shelf
and slope, and the polar band. The two weaker figures are disclosure
fields; a receipt that drops them fails whatever its headline number.
The reference month anchors are TWO-SIDED, so an inflated claim fails
the same as a broken one.

**Reference run (2026-09-01, cached native granules, month 2009-12).**
Open-ocean interior at 351 m: r = 0.9242 over 20,771 cells, median
absolute difference 1.58E-03 m per s. Full band: r = 0.7921 (shelf and
slope cells, where friction and boundary currents break the balance
test, drag it). Polar band: r = -0.06, reported and not validated.
Thermal wind identity 351 to 722 m: r = 0.6102. Attester PASS on the
run; FAIL demonstrated on a doctored r of 0.995 and on a dropped polar
disclosure. This scheme is correlation-grade; the tutorial's staggered
helper reaches 0.998 on the same comparison, the bar an implementation
using ecco_po_tutorials should be held to.[^ecco-skills-corroboration]
The contract binds the receipt to THIS method's measured numbers, not
to the stronger method's.[^tutorial-geostrophic]

**Data provenance.** The receipt also carries a `data` block: the data
root and the `RECORD.json` stamp the verify tool leaves in a tree it has
checked against its manifest (record name, manifest SHA-256,
verification time, report SHA-256). The attester refuses a receipt
whose `data.record` is not that stamp, so nothing is attested against a
tree this bundle has not manifested and verified. The two trees and
the rule are in docs/science-record.md.

[^tutorial-geostrophic]: ECCO v4 tutorial geostrophic balance chapter
[^density-factor]: gotchas/ecco-geostrophic-density-factor.md
[^phihyd-surface]: gotchas/ecco-phihyd-surface-pressure.md, measured r -0.04 without the surface term
[^ecco-skills-corroboration]: podaac/ecco-skills geostrophic acceptance record, the 0.998 tutorial-helper bar
